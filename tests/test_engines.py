import pytest
from unittest.mock import patch, MagicMock
from src.ffmpeg_engine import compile_video, MissingAssetError


def test_missing_image_raises_error(tmp_path):
    config = {
        "project_id": "test",
        "canvas_format": "landscape",
        "background_music": "fake_music.mp3",
        "global_music_volume_db": -18.0,
        "scenes": [
            {
                "sequence": 1,
                "text": "test",
                "image_path": "nonexistent_image.png",
                "voiceover_path": "nonexistent_audio.mp3",
            }
        ],
        "youtube_metadata": {},
    }

    with pytest.raises(MissingAssetError) as excinfo:
        compile_video(config, "output.mp4")
    assert "Missing image asset" in str(excinfo.value)


@patch("src.ffmpeg_engine.ffmpeg")
@patch("src.ffmpeg_engine.get_audio_duration", return_value=5.0)
@patch("src.ffmpeg_engine.os.path.exists", return_value=True)
def test_compile_video_logic(mock_exists, mock_get_audio_duration, mock_ffmpeg):
    config = {
        "project_id": "test",
        "canvas_format": "landscape",
        "background_music": "fake_music.mp3",
        "global_music_volume_db": -18.0,
        "scenes": [
            {
                "sequence": 1,
                "text": "test",
                "image_path": "fake_image.png",
                "voiceover_path": "fake_audio.mp3",
            }
        ],
        "youtube_metadata": {},
    }

    # We mock the chainable ffmpeg API structure
    mock_node = MagicMock()
    mock_node.filter.return_value = mock_node
    mock_ffmpeg.input.return_value = mock_node
    mock_ffmpeg.concat.return_value = mock_node
    mock_ffmpeg.filter.return_value = mock_node

    mock_out = MagicMock()
    mock_ffmpeg.output.return_value = mock_out
    mock_ffmpeg.overwrite_output.return_value = mock_out

    compile_video(config, "test_out.mp4")

    # Verify ffmpeg execution happened
    mock_out.run.assert_called_once_with(quiet=True)


@patch("src.ffmpeg_engine.ffmpeg")
@patch("src.ffmpeg_engine.get_audio_duration", return_value=5.0)
@patch("src.ffmpeg_engine.os.path.exists", return_value=True)
def test_compile_video_with_transitions(mock_exists, mock_get_audio_duration, mock_ffmpeg):
    config = {
        "project_id": "test",
        "canvas_format": "landscape",
        "transition_duration": 1.0,
        "scenes": [
            {
                "sequence": 1,
                "text": "test 1",
                "image_path": "fake_image_1.png",
                "voiceover_path": "fake_audio_1.mp3",
            },
            {
                "sequence": 2,
                "text": "test 2",
                "image_path": "fake_image_2.png",
                "voiceover_path": "fake_audio_2.mp3",
            }
        ]
    }

    mock_node = MagicMock()
    mock_node.filter.return_value = mock_node
    mock_ffmpeg.input.return_value = mock_node
    mock_ffmpeg.concat.return_value = mock_node
    mock_ffmpeg.filter.return_value = mock_node

    mock_out = MagicMock()
    mock_ffmpeg.output.return_value = mock_out
    mock_ffmpeg.overwrite_output.return_value = mock_out

    compile_video(config, "test_out_transition.mp4")

    mock_out.run.assert_called_once_with(quiet=True)
    # verify that filter was called for xfade/acrossfade
    filter_calls = [call.args[1] for call in mock_ffmpeg.filter.mock_calls if len(call.args) > 1 and call.args[1] in ('xfade', 'acrossfade')]
    assert 'xfade' in filter_calls
    assert 'acrossfade' in filter_calls
