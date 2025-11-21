from jwt import PyJWTError
from fastapi import HTTPException, status
from starlette.requests import Request
from app.config import settings
import jwt

def get_current_user_id(request: Request) -> str:
    # Extract JWT from authorization header
    token = request.headers.get('Authorization')
    if not token:
        raise HTTPException(
            status_code =status.HTTP_401_UNAUTHORIZED,
            detail ="Not authenticated: Missing or invalid token"
        )
    
    # Decode and validate JWT 
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token payload"
            )
        return user_id
    except PyJWTError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: Token expired or invalid signature"
        )