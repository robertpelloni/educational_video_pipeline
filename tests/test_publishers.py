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

def test_twitter_publisher(mock_video_path):
    metadata = {"title": "Test"}
    result = twitter_upload(mock_video_path, metadata)
    assert result == "stub_x_id"

def test_missing_video():
    metadata = {"title": "Test"}
    with pytest.raises(FileNotFoundError):
        tiktok_upload("nonexistent.mp4", metadata)
