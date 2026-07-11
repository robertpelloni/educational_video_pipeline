import pytest
from unittest.mock import patch, MagicMock
from src.tiktok_publisher import upload_video as tiktok_upload
from src.instagram_publisher import upload_video as instagram_upload

# Testing for Missing TikTok token execution
@patch("src.tiktok_publisher.os.environ.get")
@patch("src.tiktok_publisher.requests.post")
def test_tiktok_publisher_missing_token_executes_stub(mock_post, mock_env_get, tmp_path):
    mock_env_get.return_value = None

    video_path = tmp_path / "video.mp4"
    video_path.touch()

    # Should fall back to stub, return "stub_tiktok_id", and not call requests.post
    result = tiktok_upload(str(video_path), {"title": "Test", "description": "Desc", "tags": []})
    assert result == "stub_tiktok_id"
    mock_post.assert_not_called()

# Testing API token expiration (HTTP 401) catching for TikTok
@patch("src.tiktok_publisher.os.environ.get")
@patch("src.tiktok_publisher.requests.post")
def test_tiktok_publisher_handles_401_gracefully(mock_post, mock_env_get, tmp_path):
    mock_env_get.side_effect = lambda key: "fake_token" if key == "TIKTOK_ACCESS_TOKEN" else "fake_open_id"

    video_path = tmp_path / "video.mp4"
    video_path.touch()

    # Simulate a 401 Unauthorized response from requests
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"error_code": -1, "error_msg": "Token Expired"}
    mock_post.return_value = mock_response
    import requests
    mock_response.raise_for_status.side_effect = requests.RequestException("HTTP 401 Unauthorized")

    with pytest.raises(RuntimeError) as exc_info:
        tiktok_upload(str(video_path), {"title": "Test", "description": "Desc", "tags": []})

    assert "Failed to publish to TikTok" in str(exc_info.value)
    assert "HTTP 401" in str(exc_info.value)

# Testing API token expiration (HTTP 401) catching for Instagram
@patch("src.instagram_publisher.os.environ.get")
@patch("src.instagram_publisher.requests.post")
def test_instagram_publisher_handles_401_gracefully(mock_post, mock_env_get, tmp_path):
    mock_env_get.side_effect = lambda key: "fake_token" if key == "IG_ACCESS_TOKEN" else "fake_user_id"

    video_path = tmp_path / "video.mp4"
    video_path.touch()

    # Simulate a 401 Unauthorized response from requests
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_post.return_value = mock_response
    import requests
    mock_response.raise_for_status.side_effect = requests.RequestException("HTTP 401 Unauthorized")

    with pytest.raises(RuntimeError) as exc_info:
        instagram_upload(str(video_path), {"title": "Test", "description": "Desc", "tags": []})

    assert "Failed to publish to Instagram" in str(exc_info.value)
    assert "HTTP 401" in str(exc_info.value)


from src.twitter_publisher import upload_video as twitter_upload

@pytest.fixture
def mock_video_path(tmp_path):
    video = tmp_path / "test_video.mp4"
    video.write_text("fake video content")
    return str(video)

@patch("src.tiktok_publisher.get_tiktok_credentials")
def test_tiktok_publisher_stub_fallback(mock_get_creds, mock_video_path):
    mock_get_creds.return_value = None
    metadata = {"title": "Test"}
    result = tiktok_upload(mock_video_path, metadata)
    assert result == "stub_tiktok_id"

@patch("src.tiktok_publisher.get_tiktok_credentials")
@patch("src.tiktok_publisher.requests.post")
def test_tiktok_publisher_real_execution(mock_post, mock_get_creds, mock_video_path):
    mock_get_creds.return_value = ("fake_token", "fake_open_id")

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "error_code": 0,
        "data": {"share_id": "real_tiktok_id_123"},
    }
    mock_post.return_value = mock_response

    metadata = {"title": "Test"}
    result = tiktok_upload(mock_video_path, metadata)
    assert result == "real_tiktok_id_123"
    mock_post.assert_called_once()

@patch("src.instagram_publisher.get_instagram_credentials")
def test_instagram_publisher_stub_fallback(mock_get_creds, mock_video_path):
    mock_get_creds.return_value = None
    metadata = {"title": "Test"}
    result = instagram_upload(mock_video_path, metadata)
    assert result == "stub_ig_id"

@patch("src.instagram_publisher.time.sleep", return_value=None)
@patch("src.instagram_publisher.get_instagram_credentials")
@patch("src.instagram_publisher.requests.post")
def test_instagram_publisher_real_execution(
    mock_post, mock_get_creds, mock_sleep, mock_video_path
):
    mock_get_creds.return_value = ("fake_token", "fake_user_id")

    # We need to mock two sequential POST requests (container creation, then publish)
    mock_response_1 = MagicMock()
    mock_response_1.json.return_value = {"id": "container_123"}

    mock_response_2 = MagicMock()
    mock_response_2.json.return_value = {"id": "real_ig_media_456"}

    mock_post.side_effect = [mock_response_1, mock_response_2]

    metadata = {"title": "Test IG"}
    result = instagram_upload(mock_video_path, metadata)
    assert result == "real_ig_media_456"
    assert mock_post.call_count == 2

def test_missing_video():
    metadata = {"title": "Test"}
    with pytest.raises(FileNotFoundError):
        tiktok_upload("nonexistent.mp4", metadata)

@patch("src.twitter_publisher.get_twitter_client")
def test_twitter_publisher_with_stub_fallback(mock_get_client, mock_video_path):
    # Simulate missing credentials returning None
    mock_get_client.return_value = None

    metadata = {"title": "Test"}
    result = twitter_upload(mock_video_path, metadata)
    assert result == "stub_x_id"

@patch("src.twitter_publisher.get_twitter_client")
def test_twitter_publisher_real_execution(mock_get_client, mock_video_path):
    mock_client = MagicMock()
    mock_api = MagicMock()

    # Mock media upload response
    mock_media = MagicMock()
    mock_media.media_id = "12345"
    mock_api.media_upload.return_value = mock_media

    # Mock tweet creation response
    mock_response = MagicMock()
    mock_response.data = {"id": "98765"}
    mock_client.create_tweet.return_value = mock_response

    mock_get_client.return_value = (mock_client, mock_api)

    metadata = {"title": "Real Test", "tags": ["tag1", "tag2"]}
    result = twitter_upload(mock_video_path, metadata)

    assert result == "98765"
    mock_api.media_upload.assert_called_once_with(
        filename=mock_video_path, media_category="tweet_video"
    )
    mock_client.create_tweet.assert_called_once()
