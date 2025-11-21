from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.requests import Request
from app.utility.client import clientInit
from app.router.authentication import getUser
from app.recommendation.recommendationEngine import user_preference

router = APIRouter(tags=["preference_calculator"])

@router.get("/calculate-preference/{user_id}")
async def calculate_preference(user_id: str, request: Request):
    # Client initialization
    client = clientInit()
    db = client.spotify
    collection = db['track_history']

    # Get user data
    access_token = request.headers.get('Authorization')
    user_data = getUser(access_token)

    if user_data is None:
        return JSONResponse(
            status_code=403,
            content={"message": "User validation failed, Check token validity or network,"}
        )
    
    if user_data.get('id') != user_id:
        return JSONResponse(
            status_code=403,
            content={"message": "Forbidden access. Token ID does not match"}
        )

    # Query filter
    query_filter = {"user_id": user_id}

    # Get track histories
    user_track_history_cursor = collection.find(query_filter).sort('createdAt', -1).limit(20) 
    user_track_history = await user_track_history_cursor.to_list()

    # Calculate profile vector
    user_preference_profile = await user_preference(user_track_history) 
    
    # Define the update action (e.g., set new fields or change existing ones)
    update_action = {"$set": {
        "profile_vector": user_preference_profile
        }
    }
    
    # Execute the update with upsert=True
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
    else:
        return JSONResponse(
            status_code=200,
            content={"message": f"Matched rows: {result.matched_count}"}
        )
    
