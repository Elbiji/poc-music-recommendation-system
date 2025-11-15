from fastapi import status, APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.requests import Request
from datetime import datetime
from app.utility.client import clientInit
from app.router.authentication import getUser, refresh_access_token
from app.recommendation.songFeatures import generate_random_feature
from app.config import settings 

import pandas as pd
import requests

router = APIRouter()

def save_to_db(data, user):
    song_names = []
    artist_names = []
    played_at_list = []
    album_name = []
    danceability = []
    energy = []
    key = []
    loudness = []
    speechiness = []
    acousticness = []
    instrumentalness = []
    liveness = []
    valence = []
    tempo = []
    mode = []

    for song in data['items']:
        audio_feature = generate_random_feature()

        album_name.append(song['track']['album']['name'])
        song_names.append(song['track']['name'])
        artist_names.append(song['track']['album']['artists'][0]['name'])
        played_at_list.append(song['played_at'][0:10])

        # Pseudo random track features
        danceability.append(audio_feature.danceability)
        energy.append(audio_feature.energy)
        key.append(audio_feature.key)
        loudness.append(audio_feature.loudness)
        speechiness.append(audio_feature.speechiness)
        acousticness.append(audio_feature.acousticness)
        instrumentalness.append(audio_feature.instrumentalness)
        liveness.append(audio_feature.liveness)
        valence.append(audio_feature.valence)
        tempo.append(audio_feature.tempo)
        mode.append(audio_feature.mode)
        
    song_dict = {
        "album_name": album_name,
        "song_name": song_names,
        "artist_name": artist_names,
        "played_at": played_at_list,
        "user_id": user['id'],
        "danceability": danceability,
        "energy": energy,
        "key": key,
        "loudness": loudness,
        "speechiness": speechiness,
        "acousticness": acousticness,
        "instrumentalness": instrumentalness,
        "liveness": liveness,
        "valence": valence,
        "tempo": tempo,
        "mode": mode
    }

    songs_df = pd.DataFrame(song_dict, columns=['album_name','song_name', 'artist_name', 'played_at', 'user_id', 'danceability', 'energy', 'key', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'mode'])
    songs_df['played_at'] = pd.to_datetime(songs_df["played_at"]).dt.strftime('%d/%m/%y')
    songs_df['album_name'] = songs_df['album_name'].astype('str')
    songs_df['song_name'] = songs_df['song_name'].astype('str')
    songs_df['artist_name'] = songs_df['artist_name'].astype('str')
    songs_df['user_id'] = songs_df['user_id'].astype('str')
    songs_df['danceability'] = songs_df['danceability'].astype('float')
    songs_df['energy'] = songs_df['energy'].astype('float')
    songs_df['key'] = songs_df['key'].astype('int')
    songs_df['loudness'] = songs_df['loudness'].astype('float')
    songs_df['speechiness'] = songs_df['speechiness'].astype('float')
    songs_df['acousticness'] = songs_df['acousticness'].astype('float')
    songs_df['instrumentalness'] = songs_df['instrumentalness'].astype('float')
    songs_df['liveness'] = songs_df['liveness'].astype('float')
    songs_df['valence'] = songs_df['valence'].astype('float')
    songs_df['tempo'] = songs_df['tempo'].astype('int')
    songs_df['mode'] = songs_df['mode'].astype('int')

    client = clientInit()
    db = client.spotify

    db.track_history.insert_many(songs_df.to_dict('records')) 

@router.get('/callback')
async def callback(request: Request, code: str | None = None, error: str | None = None):
    if error:
        return JSONResponse({"error": error}, status_code=status.HTTP_400_BAD_REQUEST)
    
    if code:
        req_body = {
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': settings.REDIRECT_URI,
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET
        }

        response = requests.post(settings.TOKEN_URL, data=req_body)

        if response.status_code != 200:
            return JSONResponse({"error": "Token exchange failed"}, status_code=response.status_code)
        
        token_info = response.json()

        request.session['access_token'] = token_info.get('access_token')
        request.session['refresh_token'] = token_info.get('refresh_token')
        request.session['expires_at'] = datetime.now().timestamp() + token_info.get('expires_in')

        return RedirectResponse(url="/recently-played")

@router.get('/recently-played')
async def recently_played(request: Request):
    access_token = request.session.get('access_token')
    expires_at = request.session.get('expires_at')
    
    if not access_token:
        return RedirectResponse(url="/login")
    
    if datetime.now().timestamp() > expires_at:
        response = refresh_access_token(request.session.get['refresh_token'])

        if response == None:
            return RedirectResponse(url="/login")
        else:
            request.session.get['access_token'] = response.get('access_token')
            request.session.get['refresh_token'] = response.get('refresh_token')
            request.session.get['expires_at'] = datetime.now().timestamp() + response.get('expires_in')

    headers = {
        'Authorization': f"Bearer {access_token}"
    }

    r = requests.get(
        settings.API_BASE_URL + "me/player/recently-played",
        headers=headers
    )

    recently_played_tracks = r.json()

    save_to_db(recently_played_tracks, getUser(request.session.get('access_token')))
    return recently_played_tracks
    
    