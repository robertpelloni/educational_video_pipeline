import pytest
from unittest.mock import patch, MagicMock
from src.video_engine import compile_video, MissingAssetError, MultiplyVolume

def test_missing_image_raises_error(tmp_path):
    config = {
        "project_id": "test",
        "canvas_format": "landscape",
        "background_music": "fake_music.mp3",
        "global_music_volume": 0.12,
        "scenes": [
            {
                "sequence": 1,
                "text": "test",
                "image_path": "nonexistent_image.png",
                "voiceover_path": "nonexistent_audio.mp3"
            }
        ],
        "youtube_metadata": {}
    }

    with pytest.raises(MissingAssetError) as excinfo:
        compile_video(config, "output.mp4")
    assert "Missing image asset" in str(excinfo.value)

@patch("src.video_engine.AudioFileClip")
@patch("src.video_engine.ImageClip")
@patch("src.video_engine.os.path.exists")
def test_compile_video_logic(mock_exists, mock_image_clip, mock_audio_clip):
    # Mocking os.path.exists to always return True to pass the asset check
    mock_exists.return_value = True

    # Mock audio clip duration
    mock_audio_instance = MagicMock()
    mock_audio_instance.duration = 5.0
    mock_audio_clip.return_value = mock_audio_instance

    # Mock image clip methods
    mock_image_instance = MagicMock()
    mock_image_instance.set_duration.return_value = mock_image_instance
    mock_image_instance.resized.return_value = mock_image_instance
    mock_image_instance.set_audio.return_value = mock_image_instance
    mock_image_instance.duration = 5.0
    mock_image_clip.return_value = mock_image_instance

    config = {
        "project_id": "test",
        "canvas_format": "landscape",
        "background_music": "fake_music.mp3",
        "global_music_volume": 0.15,
        "scenes": [
            {
                "sequence": 1,
                "text": "test",
                "image_path": "fake_image.png",
                "voiceover_path": "fake_audio.mp3"
            }
        ],
        "youtube_metadata": {}
    }

    # Using another patch just to bypass actual moviepy compilation to speed up logic testing
    with patch("src.video_engine.concatenate_videoclips") as mock_concat, \
         patch("src.video_engine.CompositeAudioClip") as mock_composite, \
         patch("src.video_engine.apply_zoom_effect") as mock_zoom:

        # Configure zoom mock to return the chainable clip instance
        mock_zoom.return_value = mock_image_instance

        mock_final_video = MagicMock()
        mock_final_video.duration = 5.0
        mock_concat.return_value = mock_final_video

        # Configure a specific mock for the background music to separate it from voiceovers
        bg_music_mock = MagicMock()
        bg_music_mock.duration = 10.0
        bg_music_mock.with_effects.return_value = bg_music_mock
        bg_music_mock.set_duration.return_value = bg_music_mock

        # side_effect to return voiceover mock first, then bg music mock
        mock_audio_clip.side_effect = [mock_audio_instance, bg_music_mock]

        # Test attenuation metrics checking if volumex gets called with 0.15
        compile_video(config, "test_out.mp4")

        # Verify MultiplyVolume is called with the target volume 0.15 on the background music
        bg_music_mock.with_effects.assert_called()
        # Get all calls to with_effects
        calls = bg_music_mock.with_effects.call_args_list

        # Depending on if AudioLoop was applied (duration logic), MultiplyVolume could be in first or second call
        # Let's inspect the latest call which should be MultiplyVolume
        latest_args = calls[-1][0]
        assert isinstance(latest_args[0][0], MultiplyVolume)
        assert latest_args[0][0].factor == 0.15

        # Verify track length is matched
        mock_image_instance.set_duration.assert_called_with(5.0)
