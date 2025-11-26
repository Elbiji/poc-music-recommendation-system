from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.utility.client import clientInit
from app.model.songFeatures import generate_random_feature
from app.config import settings
from app.router.authentication import refresh_access_token 
from app.dependency import get_current_user_id
from typing import Annotated
from datetime import datetime

import pandas as pd
import requests

router = APIRouter()

async def save_to_db(data, user):
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
        "user_id": user,
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

    await db.track_history.insert_many(songs_df.to_dict('records')) 

@router.get('/recently-played')
async def recently_played(user_id: Annotated[str, Depends(get_current_user_id)]) -> JSONResponse:
    # Get access token from database
    client = clientInit()
    db = client.spotify
    collection = db['users']

    # Filter query to mongodb
    query_filter = {"user_id": user_id}

    # Get spotify's access token
    document = await collection.find_one(query_filter)   
    current_time_utc = datetime.utcnow()

    # Check if the Spotify's access_token is expired or not
    if (current_time_utc > document['access_token_expires_at']):
        # Updates database
        await refresh_access_token(user_id)
        # Retrieve newly updated database
        document = await collection.find_one(query_filter)  

    headers = {
        'Authorization': f"Bearer {document['access_token']}"
    }

    r = requests.get(
        settings.API_BASE_URL + "me/player/recently-played",
        headers=headers
    )

    recently_played_tracks = r.json()

    await save_to_db(recently_played_tracks, user_id)
    return JSONResponse(
        content=recently_played,
        status_code=status.HTTP_200_OK
    )
    
    