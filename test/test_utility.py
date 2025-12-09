from unittest.mock import patch

from app.utility.client import clientInit


@patch("app.utility.client.AsyncMongoClient")
def test_clientinit(mock_async_client):
    result = clientInit()

    mock_async_client.assert_called_once()
    