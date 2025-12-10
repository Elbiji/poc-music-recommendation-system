from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pandas as pd
import pytest
from fastapi import HTTPException
from requests.exceptions import RequestException

from app.dependency import get_current_user_id
from app.recommendation.recommendationEngine import recommender
from app.router.authentication import getUser, refresh_access_token
from app.router.track_history import save_to_db

TEST_USER_ID = 'test_user_123'

MOCK_QUERY_VECTOR = {
    "danceability": 0.85,
    "energy": 0.9,
    "loudness": -1.5,
    "speechiness": 0.45,
    "acousticness": 0.15,
    "instrumentalness": 0.0,
    "liveness": 0.1,
    "valence": 0.5,
    "tempo": 155,
}

MOCK_USER_DATA_FROM_SPOTIFY = {
    "user_id": TEST_USER_ID,
    "expires_in": 3600,
    "access_token": "ABCDEFG",
    "refresh_token": "ABCDEFG",
}


MOCK_USER_DATA = {
    "user_id": TEST_USER_ID,
    "access_token_expires_at": datetime.utcnow() + timedelta(hours=1),
    "access_token": "ABCDEFG",
    "refresh_token": "ABCDEFG",
    "profile_vector": [0.1, 0.2, 0.3],
}

MOCK_TRACK_HISTORIES = [
    {
        "_id": "1",
        "album_name": "x",
        "song_name": "Song 1",
        "artist_name": "A",
        "user_id": "u1",
        "played_at": "now",
        "danceability": 0.70,
        "energy": 0.70,
        "acousticness": 0.70,
    },
    {
        "_id": "2",
        "album_name": "y",
        "song_name": "Song 2",
        "artist_name": "B",
        "user_id": "u1",
        "played_at": "then",
        "danceability": 0.70,
        "energy": 0.70,
        "acousticness": 0.70,
    },
]

MOCK_DF_SONGS = pd.DataFrame(
    {
        "song_name": ["A", "B", "C", "D", "E"],
        "key": [1, 2, 3, 4, 5],
        "mode": [0, 1, 0, 1, 0],
        "danceability": [0.1, 0.9, 0.5, 0.6, 0.7],
        "energy": [0.2, 0.8, 0.4, 0.7, 0.3],
        "loudness": [-10.0, -1.0, -5.0, -8.0, -3.0],
        "speechiness": [0.05, 0.5, 0.1, 0.3, 0.2],
        "acousticness": [0.9, 0.1, 0.5, 0.2, 0.8],
        "instrumentalness": [0.0, 0.0, 0.0, 0.0, 0.0],
        "liveness": [0.1, 0.1, 0.1, 0.1, 0.1],
        "valence": [0.5, 0.5, 0.5, 0.5, 0.5],
        "tempo": [100, 150, 120, 90, 140],
    }
)



EXPECTED_PREFERENCE_PROFILE = {
    "danceability": 0.70,
    "energy": 0.70,
    "acousticness": 0.70,
}


@pytest.fixture
def recommender_fixture():
    recommender_instance = recommender()
    yield recommender_instance

# ========================== (Recommendation Unit Testing) ========================== 

# Mark test as async
@pytest.mark.asyncio
# Patch pd.read_csv to hit pd.read_csv
# Inject 2nd Argument
@patch(
    "app.recommendation.recommendationEngine.pd.read_csv",
    return_value=MOCK_DF_SONGS.copy(),
)
# Patch StandardScaler to hit import module of StandardScaler
# Inject 1st Argument
@patch("app.recommendation.recommendationEngine.StandardScaler")
async def test_recommendation_processor_returns_top_5_correctly(
    mock_scaler_class, mock_read_csv
):
    # Setting up mockup object for when StandardScaler
    mock_scaler_instance = MagicMock()
    # Set the fit_transform.side_effect to return the input as it is
    mock_scaler_instance.fit_transform.side_effect = lambda x: x
    # When StandardScaler is invoked, it will use the newly configured mock_scaler_instance
    mock_scaler_class.return_value = mock_scaler_instance

    top_5 = await recommender.recommendation_processor(MOCK_QUERY_VECTOR)

    assert isinstance(top_5, pd.DataFrame)
    assert len(top_5) == 5

    assert top_5.iloc[0]["song_name"] == "B"

    assert "similarity" in top_5.columns

    assert "key" not in top_5.columns
    assert "mode" not in top_5.columns

    assert top_5.iloc[0]["similarity"] >= top_5.iloc[1]["similarity"]
    assert top_5.iloc[-1]["similarity"] <= top_5.iloc[-2]["similarity"]


@pytest.mark.asyncio
async def test_calculate_user_preference():
    preference_profile = await recommender.user_preference(MOCK_TRACK_HISTORIES.copy())

    assert isinstance(preference_profile, dict)
    assert "_id" not in preference_profile
    assert "album_name" not in preference_profile
    assert "song_name" not in preference_profile
    assert "artist_name" not in preference_profile
    assert "user_id" not in preference_profile
    assert "played_at" not in preference_profile

    assert (
        preference_profile["danceability"]
        == EXPECTED_PREFERENCE_PROFILE["danceability"]
    )
    assert preference_profile["energy"] == EXPECTED_PREFERENCE_PROFILE["energy"]
    assert (
        preference_profile["acousticness"]
        == EXPECTED_PREFERENCE_PROFILE["acousticness"]
    )

# ========================== (Generate Random Unit Testing) ========================== 

@pytest.mark.asnycio
@patch("app.router.track_history.generate_random_feature")
@patch("app.router.track_history.clientInit")
async def test_save_to_db(mock_clientInit, mock_generate_random_feature):

    mock_feature = MagicMock()
    mock_feature.danceability = 0.5
    mock_feature.energy = 0.6
    mock_feature.key = 5
    mock_feature.loudness = -8.0
    mock_feature.speechiness = 0.1
    mock_feature.acousticness = 0.3
    mock_feature.instrumentalness = 0.0
    mock_feature.liveness = 0.2
    mock_feature.valence = 0.7
    mock_feature.tempo = 120
    mock_feature.mode = 1
    mock_generate_random_feature.return_value = mock_feature

    test_data = {
        "items": [
            {
                "track": {
                    "name": "Test Song 1",
                    "album": {
                        "name": "Test Album 1",
                        "artists": [{"name": "Test Artist 1"}]
                    }
                },
                "played_at": "2024-01-15T10:30:00Z"
            },
            {
                "track": {
                    "name": "Test Song 2",
                    "album": {
                        "name": "Test Album 2",
                        "artists": [{"name": "Test Artist 2"}]
                    }
                },
                "played_at": "2024-01-16T14:20:00Z"
            }
        ]
    }

    mock_insert_result = MagicMock()
    mock_insert_result.inserted_ids = ["id1", "id2"]
    mock_insert_result.acknowledged = True

    mock_track_history = MagicMock()
    mock_track_history.insert_many = AsyncMock(return_value=mock_insert_result) 

    mock_db = MagicMock()
    mock_db.track_history = mock_track_history

    mock_clientInit.return_value.spotify = mock_db 

    await save_to_db(test_data, "test_user_123")

    # ASSERT
    call_args = mock_track_history.insert_many.call_args
    inserted_data = call_args[0][0]

    mock_track_history.insert_many.assert_called_once()

    assert len(inserted_data) == 2

    assert inserted_data[0]["song_name"] == "Test Song 1"
    assert inserted_data[0]["artist_name"] == "Test Artist 1"
    assert inserted_data[0]["album_name"] == "Test Album 1"
    assert inserted_data[0]["user_id"] == "test_user_123"
    assert inserted_data[0]["danceability"] == 0.5
    assert inserted_data[0]["energy"] == 0.6
    assert inserted_data[0]["played_at"] == "15/01/24" 

    assert inserted_data[1]["song_name"] == "Test Song 2"
    assert inserted_data[1]["played_at"] == "16/01/24"

    assert mock_generate_random_feature.call_count == 2

# ========================== (Dependency Unit Testing) ========================== 

def test_dependency_fail():
    mock_request = MagicMock()
    mock_request.headers.get.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(mock_request)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated: Missing or invalid token"

@patch("app.dependency.jwt.decode")
def test_dependency_fail_decode(mock_jwt_decoder):
    mock_request = MagicMock()
    mock_request.headers.get.return_value = {
        'Authorization': {
            'user_id': "None",
            'exp_date': datetime.utcnow() + timedelta(hours=1)
        }
    }

    mock_jwt_decoder.return_value = {
        'user_id': None,
        'exp_date': datetime.utcnow() + timedelta(hours=1)
    }

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(mock_request)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication token payload"
    
@patch("app.dependency.jwt.decode")
def test_dependency_succesfull(mock_jwt_decoder):
    mock_request = MagicMock()
    mock_request.headers.get.return_value = {
        'Authorization': {
            'user_id': "test_user_123",
            'exp_date': datetime.utcnow() + timedelta(hours=1)
        }
    }

    mock_jwt_decoder.return_value = {
        'user_id': "test_user_123",
        'exp_date': datetime.utcnow() + timedelta(hours=1)
    }

    result =  get_current_user_id(mock_request)

    assert result == "test_user_123"

@patch("app.dependency.jwt.decode", side_effect=jwt.exceptions.ExpiredSignatureError)
def test_dependency_token_expired(mock_jwt_decoder):
    mock_request = MagicMock()
    mock_request.headers.get.return_value = {
        'Authorization': {
            'user_id': "test_user_123",
            'exp_date': datetime.utcnow() - timedelta(hours=1)
        }
    }

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(mock_request)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials: Token expired or invalid signature"

# ========================== (Authentication Unit Testing) ========================== 

def test_get_user_no_access_token():
    mock_access_token = None

    user = getUser(mock_access_token)

    assert  user is None

@patch("app.router.authentication.requests.get")
def test_get_user_token_valid_200(mock_get):
    mock_access_token = "FAKE TOKEN"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_USER_DATA
    mock_get.return_value = mock_response

    user = getUser(mock_access_token)

    assert user["user_id"] == TEST_USER_ID
    assert user["access_token"] == MOCK_USER_DATA["access_token"]


@patch("app.router.authentication.requests.get")
def test_get_user_token_valid_401(mock_get):
    mock_access_token = "FAKE TOKEN"
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = MOCK_USER_DATA
    mock_get.return_value = mock_response

    user = getUser(mock_access_token)

    assert user.status_code == 401

@patch("app.router.authentication.requests.get")
def test_get_user_token_valid_500(mock_get):
    mock_access_token = "FAKE TOKEN"
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = MOCK_USER_DATA
    mock_get.return_value = mock_response

    user = getUser(mock_access_token)

    assert user.status_code == 500

@patch("app.router.authentication.requests.get", side_effect=RequestException)
def test_get_user_token_valid_Request_Exception(mock_get):
    mock_access_token = "FAKE TOKEN"
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = MOCK_USER_DATA
    mock_get.return_value = mock_response

    with pytest.raises(HTTPException) as exc_info:
        getUser(mock_access_token)

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Network error while reaching Spotify."

@patch("app.router.authentication.requests.post")
@patch("app.router.authentication.clientInit")
async def test_refresh_access_token_400(mock_clientInit, mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 400

    mock_post.return_value = mock_response

    mock_users_collection = MagicMock()
    mock_users_collection.find_one = AsyncMock(return_value=MOCK_USER_DATA)

    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(
        side_effect=lambda key: {
            "users": mock_users_collection,
        }[key]
    )

    mock_db.users = mock_users_collection

    mock_clientInit.return_value.spotify = mock_db

    response = await refresh_access_token(TEST_USER_ID)

    assert response.status_code == 401

@patch("app.router.authentication.requests.post")
@patch("app.router.authentication.clientInit")
async def test_refresh_access_token_500(mock_clientInit, mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 500

    mock_post.return_value = mock_response

    mock_users_collection = MagicMock()
    mock_users_collection.find_one = AsyncMock(return_value=MOCK_USER_DATA)

    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(
        side_effect=lambda key: {
            "users": mock_users_collection,
        }[key]
    )

    mock_db.users = mock_users_collection

    mock_clientInit.return_value.spotify = mock_db

    response = await refresh_access_token(TEST_USER_ID)

    assert response.status_code == 500

@patch("app.router.authentication.requests.post", side_effect=RequestException)
@patch("app.router.authentication.clientInit")
async def test_refresh_access_token_503(mock_clientInit, mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 500

    mock_post.return_value = mock_response

    mock_users_collection = MagicMock()
    mock_users_collection.find_one = AsyncMock(return_value=MOCK_USER_DATA)

    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(
        side_effect=lambda key: {
            "users": mock_users_collection,
        }[key]
    )

    mock_db.users = mock_users_collection

    mock_clientInit.return_value.spotify = mock_db

    with pytest.raises(HTTPException) as exc_info:
        await refresh_access_token(TEST_USER_ID)

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Network error while reaching Spotify."

@patch("app.router.authentication.requests.post")
@patch("app.router.authentication.jwt.encode")
@patch("app.router.authentication.clientInit")
async def test_refresh_access_token_200(mock_clientInit, mock_encode, mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_USER_DATA_FROM_SPOTIFY

    mock_update_result = MagicMock()
    mock_update_result.acknowledged = True
    mock_update_result.matched_count = 1

    mock_post.return_value = mock_response

    mock_encode.return_value = "encoded_payload"  

    mock_users_collection = MagicMock()
    mock_users_collection.find_one = AsyncMock(return_value=MOCK_USER_DATA)
    mock_users_collection.update_one = AsyncMock(return_value=mock_update_result)

    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(
        side_effect=lambda key: {
            "users": mock_users_collection,
        }[key]
    )

    mock_db.users = mock_users_collection

    mock_clientInit.return_value.spotify = mock_db

    response = await refresh_access_token(TEST_USER_ID)

    assert response.status_code == 200

