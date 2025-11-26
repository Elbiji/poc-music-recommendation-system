from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.utility.client import clientInit
from app.router.authentication import refresh_access_token
from app.recommendation.recommendationEngine import recommender_instance
from app.dependency import get_current_user_id
from typing import Annotated
from datetime import datetime

router = APIRouter(tags=["recommendation"])

@router.get("/get-recommendation")
async def get_recommendation(user_id: Annotated[str, Depends(get_current_user_id)]) -> JSONResponse:
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

    # Get user's profile vector
    document = await collection.find_one(query_filter)

    songs = await recommender.recommendation_processor(document['profile_vector'])
    songs = songs.to_dict('records')

    return JSONResponse(
        content={
            "recommendations": songs
        },
        status_code=status.HTTP_200_OK
    )

