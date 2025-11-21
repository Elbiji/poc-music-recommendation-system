from fastapi import status, APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
from app.config import settings 
from requests.exceptions import RequestException
from datetime import datetime, timedelta
from app.utility.client import clientInit
import urllib.parse
import requests
import jwt

router = APIRouter(tags=["authentication"])

def getUser(access_token: str) -> JSONResponse:
    if not access_token:
        print("Error: Access token is missing")
        return None

    headers = {
        'Authorization': f"Bearer {access_token}"
    }

    try:
        response = requests.get(
            settings.API_BASE_URL + "me",
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "Invalid access token for accessing Spotify API service."}
            )
        else:
            return JSONResponse(
                status_code=response.status_code,
                content={"message": "Spotify API error."}
            )
    except RequestException as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"message": "Network error while reaching Spotify."}
        )

async def refresh_access_token(user_id: str) -> JSONResponse:
    client = clientInit()
    db = client.spotify
    collection = db['users']

    # Filter query to mongodb
    query_filter = {"user_id": user_id}

    document = await collection.find_one(query_filter)

    refresh_token = document['refresh_token']
    
    req_body = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET
    }

    try:
        response = requests.post(settings.TOKEN_URL, data=req_body)

        # Update database
        if response.status_code == 200:
            # Retrieving data from response
            token_info = response.json()

            update_action = {
                "$set": {
                    "access_token": token_info.get('access_token'),
                    "refresh_token": token_info.get('refresh_token'),
                    "access_token_expires_at": datetime.utcnow() + timedelta(seconds=token_info.get('expires_in'))
                }
            }

            await db.users.update_one(
                query_filter,
                update_action,
                upsert=True
            )

            # JWT
            payload = {
                'user_id': user_id,
                'exp': datetime.utcnow() + timedelta(hours=1)
            }

            jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

            return JSONResponse(
                content={
                    "message": "Spotify session refreshed succesfully.",
                    "auth_token": jwt_token,
                },
                status_code=status.HTTP_200_OK
            )
        elif response.status_code == 400:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "Invalid access token for accessing Spotify API service."}
            )
        else:
            return JSONResponse(
                status_code=response.status_code,
                content={"message": "Spotify API error."}
            )
    except RequestException:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"message": "Network error while reaching Spotify."}
        )
        

@router.get("/login")
async def login():
    scope = 'user-read-private user-read-email user-top-read user-read-recently-played'

    params = {
        'client_id': settings.CLIENT_ID,
        'response_type': 'code',
        'scope' : scope,
        'redirect_uri' : settings.REDIRECT_URI,
        'show_dialog' : True
    }

    auth_url = f"{settings.AUTH_URL}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(auth_url)

@router.get('/callback')
async def callback(code: str | None = None, error: str | None = None) -> JSONResponse:
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
        
        # Setting up important credential datas
        token_info = response.json()
        access_token = token_info.get('access_token')
        refresh_token = token_info.get('refresh_token')
        expires_in = token_info.get('expires_in')
        user_data = getUser(access_token)
        user_id = user_data.get('id')

        # Save user Spotify's credential and tokens to db
        client = clientInit()
        db = client.spotify

        # Query filter
        query_filter = {"user_id": user_id}

        if expires_in:
            # Use datetime.utcnow() for consistency
            access_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        else:
            access_token_expires_at = None

        update_action = {
            "$set": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "access_token_expires_at": access_token_expires_at
            },
            "$setOnInsert": {
                "user_id": user_id, 
                "display_name": user_data.get('display_name'),
                "explicit_content": user_data.get('explicit_content'),
                "followers": user_data.get('followers'),
                "type": user_data.get('type'),
                "product": user_data.get('product'),
                "email": user_data.get('email'),
                "created_at": datetime.now(),
            }
        }

        # Querying to database
        result = await db.users.update_one(
            query_filter,
            update_action,
            upsert=True
        )

        if not result.acknowledged:
            return JSONResponse(
                status_code=500,
                content={"message": "Mongodb internal server error"}
        )

        # JWT
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }

        jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        return JSONResponse(
            content={
                "message": "Authentication succesfull",
                "auth_token": jwt_token,
            },
            status_code=status.HTTP_200_OK
        )