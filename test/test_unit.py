from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.recommendation.recommendationEngine import recommender

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


EXPECTED_PREFERENCE_PROFILE = {
    "danceability": 0.70,
    "energy": 0.70,
    "acousticness": 0.70,
}


@pytest.fixture
def recommender_fixture():
    recommender_instance = recommender()
    yield recommender_instance


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
