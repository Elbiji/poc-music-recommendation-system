from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse
from app.router import authentication, track_history, recommendation, calculate_preference

app = FastAPI(
    title="Music Recommendation API",
    description="API for Spotify recommendation and track history."
)

app.include_router(authentication.router)
app.include_router(track_history.router)
app.include_router(recommendation.router)
app.include_router(calculate_preference.router)

# app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

@app.get("/", tags=["root"])
async def root():
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

APP_MODULE = "app.main:app"

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))

#     uvicorn.run(
#         APP_MODULE,
#         host="0.0.0.0",
#         port=port,
#         reload=True
#     )