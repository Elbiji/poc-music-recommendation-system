from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from app.config import settings 
import urllib.parse
import requests
from requests.exceptions import RequestException

router = APIRouter(tags=["authentication"])

def getUser(access_token: str):
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
            print(f"Error: Invalid token (Status {response.status_code}).")
            return None
        else:
            print(f"Error: Spotify API returned unexpected status {response.status_code}.")
            return None
    except RequestException as e:
        print(f"Network error while fetching user data: {e}")
        return None

def refresh_access_token(refresh_token: str):
    req_body = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET
    }
    
    response = requests.post(settings.TOKEN_URL, data=req_body)
    
    if response.status_code != 200:
        return None
    
    return response.json()

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
