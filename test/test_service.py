from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.dependency import get_current_user_id
from app.main import app
from app.router.authentication import callback

TEST_USER_ID = 'test_user_123'
MOCK_SONGS = [{"song": "A"}, {"song": "B"}]
MOCK_PROFILE_VECTOR = {
    "danceability": 0.1,
    "energy": 0.2,
    "key": 1,
    "loudness": -10.0,
    "speechiness": 0.05,
    "acousticness": 0.9,
    "instrumentalness": 0.0,
    "liveness": 0.1,
    "valence": 0.5,
    "tempo": 100,
    "mode": 0,
}

MOCK_USER_TOKEN = {
    "id": TEST_USER_ID,
    "expires_in": 3600,
    "access_token": "ABCDEFG",
    "refresh_token": "ABCDEFG",
}

MOCK_USER_TOKEN_CORRUPTED = {
    "id": TEST_USER_ID,
    "expires_in": None,
    "access_token": "ABCDEFG",
    "refresh_token": "ABCDEFG",
}

MOCK_USER_DATA_FROM_SPOTIFY = {
    "display_name": "MEBOMBO",
    "explicit_content": True,
    "followers": 26,
    "type": None,
    "product": "premium",
    "email": "mebombo@gmail.com"
}

# Setup TestClient so testing can call internal endpoints
@pytest.fixture
def client():
    # Automatic resource management using with, it ensures the connection will close automatically
    with TestClient(app=app, base_url="http://test") as c:
        yield c


# Replaces FastAPI's dependency
@pytest.fixture
def override_user_dependency():
    async def mock_get_current_user_id():
        return TEST_USER_ID

    app.dependency_overrides[get_current_user_id] = mock_get_current_user_id
    yield
    app.dependency_overrides.clear()


# Configuring recommendation_processor to be reusable for the entire test
@pytest.fixture(autouse=True)
def mock_recommender():
    # Configure Mockup object
    mock_df_return = MagicMock()
    mock_df_return.to_dict.return_value = MOCK_SONGS
    # Automatic resource management using with, it ensures the original method is returned
    with patch(
        "app.router.recommendation.recommender.recommendation_processor",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = (
            mock_df_return  # Assign the configured mockup to the newly created mockup
        )
        yield mock

# ========================== (/get-recommendation) ==========================

@patch("app.router.recommendation.refresh_access_token", new_callable=AsyncMock)
@patch("app.router.recommendation.clientInit")
async def test_get_recommendation_token_valid(
    mock_clientInit, mock_refresh_access_token, client, override_user_dependency
):
    valid_document = {
        "user_id": TEST_USER_ID,
        "access_token_expires_at": datetime.utcnow() + timedelta(hours=1),
        "profile_vector": [0.1, 0.2, 0.3],
    }

    # Pathing the MongoDB mockup
    # Creating async object for the find_one method
    mock_collection = AsyncMock()
    # Creating the return value for the find_one
    mock_collection.find_one.return_value = valid_document
    # Replaces db = client.spotify with a predefine dictionary
    mock_clientInit.return_value.spotify = {"users": mock_collection}

    response = client.get("/get-recommendation")

    assert response.status_code == 200
    assert response.json()["recommendations"] == MOCK_SONGS

    mock_refresh_access_token.assert_not_called()

    assert mock_collection.find_one.call_count == 2


@patch("app.router.recommendation.refresh_access_token", new_callable=AsyncMock)
@patch("app.router.recommendation.clientInit")
async def test_get_recommendation_token_expired(
    mock_clientInit, mock_refresh_access_token, client, override_user_dependency
):
    expired_doc = {
        "user_id": TEST_USER_ID,
        "access_token_expires_at": datetime.utcnow() - timedelta(minutes=5),
        "profile_vector": [0.0, 0.0, 0.0],  # Old vector
    }
    refreshed_doc = {
        "user_id": TEST_USER_ID,
        "access_token_expires_at": datetime.utcnow() + timedelta(hours=1),
        "profile_vector": [1.0, 1.0, 1.0],  # New vector
    }

    # Pathing the MongoDB mockup
    # Creating async object for the find_one method
    mock_collection = AsyncMock()
    # Added sequential return value for when find_one is called
    mock_collection.find_one.side_effect = [expired_doc, refreshed_doc, refreshed_doc]
    mock_clientInit.return_value.spotify = {"users": mock_collection}
    response = client.get("/get-recommendation")

    assert response.status_code == 200
    assert response.json()["recommendations"] == MOCK_SONGS

    mock_refresh_access_token.assert_called_once_with(TEST_USER_ID)

    assert mock_collection.find_one.call_count == 3

# ========================== (/calculate_preference) ==========================

@patch("app.router.calculate_preference.clientInit")
@patch(
    "app.router.calculate_preference.recommender.user_preference",
    new_callable=AsyncMock,
)
async def test_get_calculate_preference(
    mock_user_preference,
    mock_clientInit,
    client,
    override_user_dependency,
):
    valid_document = [
        {
            "album_name": "a",
            "song_name": "a",
            "artist_name": "a",
            "played_at": "today",
            "user_id": "test_user_123",
            "danceability": 0.1,
            "energy": 0.2,
            "key": 1,
            "loudness": -10.0,
            "speechiness": 0.05,
            "acousticness": 0.9,
            "instrumentalness": 0.0,
            "liveness": 0.1,
            "valence": 0.5,
            "tempo": 100,
            "mode": 0,
        },
        {
            "album_name": "b",
            "song_name": "b",
            "artist_name": "b",
            "played_at": "today",
            "user_id": "test_user_123",
            "danceability": 0.1,
            "energy": 0.2,
            "key": 1,
            "loudness": -10.0,
            "speechiness": 0.05,
            "acousticness": 0.9,
            "instrumentalness": 0.0,
            "liveness": 0.1,
            "valence": 0.5,
            "tempo": 100,
            "mode": 0,
        },
    ]

    MOCK_MATCH_ROWS = 1

    mock_update_result = MagicMock()
    mock_update_result.acknowledged = True
    mock_update_result.matched_count = MOCK_MATCH_ROWS

    mock_user_preference.return_value = MOCK_PROFILE_VECTOR

    mock_users_collection = MagicMock()
    mock_users_collection.update_one = AsyncMock(return_value=mock_update_result)

    # Pathing the MongoDB mockup
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=valid_document)

    mock_sort = MagicMock()
    mock_sort.limit = MagicMock(return_value=mock_cursor)

    mock_find = MagicMock()
    mock_find.sort = MagicMock(return_value=mock_sort)

    mock_history_collection = MagicMock()
    mock_history_collection.find = MagicMock(return_value=mock_find)

    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(
        side_effect=lambda key: {
            "track_history": mock_history_collection,
            "users": mock_users_collection,
        }[key]
    )

    mock_db.users = mock_users_collection

    mock_clientInit.return_value.spotify = mock_db


    response = client.get("/calculate-preference")

    assert response.status_code == 200

    mock_users_collection.update_one.assert_called_once_with(
        {"user_id": TEST_USER_ID},
        {"$set": {"profile_vector": MOCK_PROFILE_VECTOR}},
        upsert=False,
    )

    assert response.json()["message"] == f"Matched rows: {MOCK_MATCH_ROWS}"

@patch("app.router.calculate_preference.clientInit")
@patch(
    "app.router.calculate_preference.recommender.user_preference",
    new_callable=AsyncMock,
)
async def test_get_calculate_preference_failed(
    mock_user_preference,
    mock_clientInit,
    client,
    override_user_dependency,
):
    valid_document = [
        {
            "album_name": "a",
            "song_name": "a",
            "artist_name": "a",
            "played_at": "today",
            "user_id": "test_user_123",
            "danceability": 0.1,
            "energy": 0.2,
            "key": 1,
            "loudness": -10.0,
            "speechiness": 0.05,
            "acousticness": 0.9,
            "instrumentalness": 0.0,
            "liveness": 0.1,
            "valence": 0.5,
            "tempo": 100,
            "mode": 0,
        },
        {
            "album_name": "b",
            "song_name": "b",
            "artist_name": "b",
            "played_at": "today",
            "user_id": "test_user_123",
            "danceability": 0.1,
            "energy": 0.2,
            "key": 1,
            "loudness": -10.0,
            "speechiness": 0.05,
            "acousticness": 0.9,
            "instrumentalness": 0.0,
            "liveness": 0.1,
            "valence": 0.5,
            "tempo": 100,
            "mode": 0,
        },
    ]

    MOCK_MATCH_ROWS = 1

    mock_update_result = MagicMock()
    mock_update_result.acknowledged = False
    mock_update_result.matched_count = MOCK_MATCH_ROWS

    mock_user_preference.return_value = MOCK_PROFILE_VECTOR

    mock_users_collection = MagicMock()
    mock_users_collection.update_one = AsyncMock(return_value=mock_update_result)

    # Pathing the MongoDB mockup
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=valid_document)

    mock_sort = MagicMock()
    mock_sort.limit = MagicMock(return_value=mock_cursor)

    mock_find = MagicMock()
    mock_find.sort = MagicMock(return_value=mock_sort)

    mock_history_collection = MagicMock()
    mock_history_collection.find = MagicMock(return_value=mock_find)

    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(
        side_effect=lambda key: {
            "track_history": mock_history_collection,
            "users": mock_users_collection,
        }[key]
    )

    mock_db.users = mock_users_collection

    mock_clientInit.return_value.spotify = mock_db


    response = client.get("/calculate-preference")

    assert response.status_code == 500

    mock_users_collection.update_one.assert_called_once_with(
        {"user_id": TEST_USER_ID},
        {"$set": {"profile_vector": MOCK_PROFILE_VECTOR}},
        upsert=False,
    )

    assert response.json()["message"] == "Mongodb internal server error"

# ========================== (/recently_played) ==========================

@patch("app.router.track_history.save_to_db", new_callable=AsyncMock)
@patch("app.router.track_history.requests.get")
@patch("app.router.track_history.refresh_access_token", new_callable=AsyncMock)
@patch("app.router.track_history.clientInit")
async def test_get_track_history_token_valid(mock_clientInit, mock_refresh_access_token, mock_get, mock_save_to_db,  client, override_user_dependency):

    valid_document = {
        "user_id": TEST_USER_ID,
        "access_token_expires_at": datetime.utcnow() + timedelta(hours=1),
        "access_token": "ABCDEFG",
        "profile_vector": [0.1, 0.2, 0.3],
    }

    MOCK_TRACK = {
        "items": [
            {
                "track": {
                    "id": "abc123",
                    "name": "Test Song",
                    "artists": [{"name": "Test Artist"}],
                    "album": {"name": "Test Album"}
                },
                "played_at": "2024-01-01T12:00:00Z"
            }
        ]
    }

    mock_users_collection = MagicMock()
    mock_users_collection.find_one = AsyncMock(return_value=valid_document)

    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(
        side_effect =lambda key: {
            "users": mock_users_collection
        }[key]
    )

    mock_clientInit.return_value.spotify = mock_db

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_TRACK
    mock_get.return_value = mock_response

    response = client.get("/recently-played")

    call_args = mock_get.call_args
    assert "me/player/recently-played" in call_args[0][0]
    assert "headers" in call_args[1]
    mock_get.assert_called_once()

    assert mock_users_collection.find_one.call_count == 1
    assert response.status_code == 200
    assert response.json() == MOCK_TRACK

@patch("app.router.track_history.save_to_db", new_callable=AsyncMock)
@patch("app.router.track_history.requests.get")
@patch("app.router.track_history.refresh_access_token", new_callable=AsyncMock)
@patch("app.router.track_history.clientInit")
async def test_get_track_history_token_expired(mock_clientInit, mock_refresh_access_token, mock_get, mock_save_to_db,  client, override_user_dependency):

    expired_doc = {
        "user_id": TEST_USER_ID,
        "access_token_expires_at": datetime.utcnow() - timedelta(minutes=5),
        "access_token": "ABCDEFG",
        "profile_vector": [0.0, 0.0, 0.0],  # Old vector
    }
    refreshed_doc = {
        "user_id": TEST_USER_ID,
        "access_token_expires_at": datetime.utcnow() + timedelta(hours=1),
        "access_token": "123456",
        "profile_vector": [1.0, 1.0, 1.0],  # New vector
    }

    MOCK_TRACK = {
        "items": [
            {
                "track": {
                    "id": "abc123",
                    "name": "Test Song",
                    "artists": [{"name": "Test Artist"}],
                    "album": {"name": "Test Album"}
                },
                "played_at": "2024-01-01T12:00:00Z"
            }
        ]
    }

    mock_users_collection = MagicMock()
    mock_users_collection.find_one = AsyncMock(side_effect=[expired_doc, refreshed_doc])

    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(
        side_effect =lambda key: {
            "users": mock_users_collection
        }[key]
    )

    mock_clientInit.return_value.spotify = mock_db

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_TRACK
    mock_get.return_value = mock_response

    response = client.get("/recently-played")

    call_args = mock_get.call_args
    assert "me/player/recently-played" in call_args[0][0]
    assert "headers" in call_args[1]
    mock_get.assert_called_once()

    assert mock_users_collection.find_one.call_count == 2
    assert response.status_code == 200
    assert response.json() == MOCK_TRACK

    mock_refresh_access_token.assert_called_once_with(TEST_USER_ID)

# ========================== (/) ========================== 

async def test_root(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers.get("location") == "/login"
    

# ========================== (/login) ========================== 

async def test_login(client):
    response = client.get("/login", follow_redirects=False)

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

# ========================== (/callback) ========================== 

# @patch("app.router.track_history.save_to_db", new_callable=AsyncMock)
# @patch("app.router.track_history.requests.get")
# @patch("app.router.track_history.refresh_access_token", new_callable=AsyncMock)
@patch("app.router.track_history.clientInit")
@patch("app.router.authentication.requests.post")
async def test_callback_400(mock_post, client):

    response = await callback(error="error")

    assert response.status_code == 400

@patch("app.router.authentication.settings")
@patch("app.router.track_history.clientInit")
@patch("app.router.authentication.requests.post")
async def test_callback_501(mock_post, client, mock_settings):

    mock_settings.REDIRECT_URI = "http://localhost:8000/callback"
    mock_settings.CLIENT_ID = "test_client_id"
    mock_settings.CLIENT_SECRET = "test_client_secret"
    mock_settings.TOKEN_URL = "api/token"

    mock_response = MagicMock()
    mock_response.status_code = 501
    mock_response.json.return_value = MOCK_USER_TOKEN

    mock_post.return_value = mock_response

    response = await callback(code="code")

    assert response.status_code == 501

@patch("app.router.authentication.jwt.encode")
@patch("app.router.authentication.getUser")
@patch("app.router.authentication.settings")
@patch("app.router.authentication.clientInit")
@patch("app.router.authentication.requests.post")
async def test_callback_500(mock_post, mock_clientInit, mock_settings, mock_getUser, mock_encode):

    mock_settings.REDIRECT_URI = "http://localhost:8000/callback"
    mock_settings.CLIENT_ID = "test_client_id"
    mock_settings.CLIENT_SECRET = "test_client_secret"
    mock_settings.TOKEN_URL = "api/token"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_USER_TOKEN

    mock_getUser.return_value = MOCK_USER_DATA_FROM_SPOTIFY 

    mock_post.return_value = mock_response

    mock_update_result = MagicMock()
    mock_update_result.acknowledged = False
    mock_update_result.matched_count = 1

    mock_users_collection = MagicMock()
    mock_users_collection.update_one = AsyncMock(return_value=mock_update_result)

    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(
        side_effect =lambda key: {
            "users": mock_users_collection
        }[key]
    )

    mock_clientInit.return_value.spotify = mock_db

    mock_encode.return_value = "encoded_payload"

    response = await callback(code="code")

    assert response.status_code == 500

@patch("app.router.authentication.jwt.encode")
@patch("app.router.authentication.getUser")
@patch("app.router.authentication.settings")
@patch("app.router.track_history.clientInit")
@patch("app.router.authentication.requests.post")
async def test_callback_200(mock_post, mock_clientInit, mock_settings, mock_getUser, mock_encode):

    mock_settings.REDIRECT_URI = "http://localhost:8000/callback"
    mock_settings.CLIENT_ID = "test_client_id"
    mock_settings.CLIENT_SECRET = "test_client_secret"
    mock_settings.TOKEN_URL = "api/token"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_USER_TOKEN

    mock_getUser.return_value = MOCK_USER_DATA_FROM_SPOTIFY 

    mock_post.return_value = mock_response

    mock_update_result = MagicMock()
    mock_update_result.acknowledged = True
    mock_update_result.matched_count = 1

    mock_users_collection = MagicMock()
    mock_users_collection.update_one = AsyncMock(return_value=mock_update_result)

    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(
        side_effect =lambda key: {
            "users": mock_users_collection
        }[key]
    )

    mock_clientInit.return_value.spotify = mock_db

    mock_encode.return_value = "encoded_payload"

    response = await callback(code="code")

    assert response.status_code == 200


