from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.utility.client import clientInit
from app.recommendation.recommendationEngine import recommender
from app.dependency import get_current_user_id
from typing import Annotated

router = APIRouter(tags=["preference_calculator"])

@router.get("/calculate-preference")
async def calculate_preference(user_id: Annotated[str, Depends(get_current_user_id)]) -> JSONResponse:
    # Get tracks from database
    client = clientInit()
    db = client.spotify
    collection = db['track_history']

    # Query filter
    query_filter = {"user_id": user_id}

    # Get track histories
    user_track_history_cursor = collection.find(query_filter).sort('createdAt', -1).limit(20) 
    user_track_history = await user_track_history_cursor.to_list()

    # Calculate profile vector
    user_preference_profile = await recommender.user_preference(user_track_history) 
    
    # Define the update action (e.g., set new fields or change existing ones)
    update_action = {"$set": {
        "profile_vector": user_preference_profile
        }
    }
    
    # Execute the update 
    result = await db.users.update_one(
        query_filter, 
        update_action, 
        upsert=False  
    )

    if not result.acknowledged:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Mongodb internal server error"}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"Matched rows: {result.matched_count}"}
        )
    
