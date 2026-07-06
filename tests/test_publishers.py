import pytest
from unittest.mock import patch, MagicMock
from src.tiktok_publisher import upload_video as tiktok_upload
from src.instagram_publisher import upload_video as instagram_upload
from src.twitter_publisher import upload_video as twitter_upload
import os

@pytest.fixture
def mock_video_path(tmp_path):
    video = tmp_path / "test_video.mp4"
    video.write_text("fake video content")
    return str(video)

def test_tiktok_publisher(mock_video_path):
    metadata = {"title": "Test"}
    result = tiktok_upload(mock_video_path, metadata)
    assert result == "stub_tiktok_id"

def test_instagram_publisher(mock_video_path):
    metadata = {"title": "Test"}
    result = instagram_upload(mock_video_path, metadata)
    assert result == "stub_ig_id"

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
    mock_response.data = {'id': '98765'}
    mock_client.create_tweet.return_value = mock_response

    mock_get_client.return_value = (mock_client, mock_api)

    metadata = {"title": "Real Test", "tags": ["tag1", "tag2"]}
    result = twitter_upload(mock_video_path, metadata)

    assert result == "98765"
    mock_api.media_upload.assert_called_once_with(filename=mock_video_path, media_category="tweet_video")
    mock_client.create_tweet.assert_called_once()
