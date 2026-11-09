import pytest
from unittest.mock import patch, MagicMock
from src.ffmpeg_engine import compile_video, MissingAssetError
from src.audio_engine import format_subtitle_cues


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

    # Verify subtitles filter was applied (because os.path.exists is mocked to True)
    # the filter is called on the node, not ffmpeg.filter
    filter_calls = [
        call
        for call in mock_node.filter.mock_calls
        if len(call.args) > 0 and call.args[0] == "subtitles"
    ]
    assert len(filter_calls) > 0
    # Verify custom styling was passed into the subtitles filter
    assert "force_style" in filter_calls[0].kwargs
    assert "FontSize=" in filter_calls[0].kwargs["force_style"]


@patch("src.ffmpeg_engine.ffmpeg")
@patch("src.ffmpeg_engine.get_audio_duration", return_value=5.0)
@patch("src.ffmpeg_engine.os.path.exists", return_value=True)
def test_compile_video_with_transitions(
    mock_exists, mock_get_audio_duration, mock_ffmpeg
):
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
            },
        ],
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
    filter_calls = [
        call.args[1]
        for call in mock_ffmpeg.filter.mock_calls
        if len(call.args) > 1 and call.args[1] in ("xfade", "acrossfade")
    ]
    assert "xfade" in filter_calls
    assert "acrossfade" in filter_calls


@patch("src.ffmpeg_engine.ffmpeg")
@patch("src.ffmpeg_engine.get_audio_duration", return_value=5.0)
@patch("src.ffmpeg_engine.os.path.exists", return_value=True)
def test_compile_video_with_canvas_format_override(
    mock_exists, mock_get_audio_duration, mock_ffmpeg
):
    config = {
        "project_id": "test",
        "canvas_format": "landscape",  # Base config says landscape
        "scenes": [
            {
                "sequence": 1,
                "text": "test 1",
                "image_path": "fake_image_1.png",
                "voiceover_path": "fake_audio_1.mp3",
            }
        ],
    }

    mock_node = MagicMock()
    mock_node.filter.return_value = mock_node
    mock_ffmpeg.input.return_value = mock_node
    mock_ffmpeg.concat.return_value = mock_node
    mock_ffmpeg.filter.return_value = mock_node

    mock_out = MagicMock()
    mock_ffmpeg.output.return_value = mock_out
    mock_ffmpeg.overwrite_output.return_value = mock_out

    # Override to portrait
    compile_video(config, "test_out_portrait.mp4", canvas_format="portrait")

    mock_out.run.assert_called_once_with(quiet=True)

    # Verify the crop filter used portrait dimensions (1080x1920)
    filter_calls = [
        call
        for call in mock_node.filter.mock_calls
        if call.args and call.args[0] == "crop"
    ]
    assert len(filter_calls) > 0
    crop_kwargs = filter_calls[0].kwargs
    assert crop_kwargs.get("w") == 1080
    assert crop_kwargs.get("h") == 1920

    # Verify canvas-adaptive subtitle font size is 28 for portrait
    sub_filter_calls = [
        call
        for call in mock_node.filter.mock_calls
        if call.args and call.args[0] == "subtitles"
    ]
    assert len(sub_filter_calls) > 0
    assert "FontSize=28" in sub_filter_calls[0].kwargs.get("force_style", "")


@patch("src.ffmpeg_engine.ffmpeg")
@patch("src.ffmpeg_engine.get_audio_duration", return_value=5.0)
@patch("src.ffmpeg_engine.os.path.exists", return_value=True)
def test_compile_video_focal_point_zoompan_coordinates(
    mock_exists, mock_get_audio_duration, mock_ffmpeg
):
    config = {
        "project_id": "test_focal",
        "canvas_format": "landscape",
        "scenes": [
            {
                "sequence": 1,
                "text": "test focal",
                "image_path": "fake_image_1.png",
                "voiceover_path": "fake_audio_1.mp3",
                "focal_point": "top",
            }
        ],
    }

    mock_node = MagicMock()
    mock_node.filter.return_value = mock_node
    mock_ffmpeg.input.return_value = mock_node
    mock_ffmpeg.concat.return_value = mock_node
    mock_ffmpeg.filter.return_value = mock_node

    mock_out = MagicMock()
    mock_ffmpeg.output.return_value = mock_out
    mock_ffmpeg.overwrite_output.return_value = mock_out

    compile_video(config, "test_out_focal.mp4")

    # Verify zoompan coordinates for 'top' focal point: y='0'
    zoompan_calls = [
        call
        for call in mock_node.filter.mock_calls
        if call.args and call.args[0] == "zoompan"
    ]
    assert len(zoompan_calls) > 0
    assert zoompan_calls[0].kwargs.get("y") == "0"
    assert zoompan_calls[0].kwargs.get("x") == "(iw-iw/zoom)/2"


@patch("src.ffmpeg_engine.ffmpeg")
@patch("src.ffmpeg_engine.get_audio_duration", return_value=5.0)
@patch("src.ffmpeg_engine.os.path.exists", return_value=True)
def test_compile_video_subtitle_font_family_and_shadow(
    mock_exists, mock_get_audio_duration, mock_ffmpeg
):
    config = {
        "project_id": "test_sub_style",
        "canvas_format": "landscape",
        "scenes": [
            {
                "sequence": 1,
                "text": "test style",
                "image_path": "fake_image_1.png",
                "voiceover_path": "fake_audio_1.mp3",
            }
        ],
    }

    mock_node = MagicMock()
    mock_node.filter.return_value = mock_node
    mock_ffmpeg.input.return_value = mock_node
    mock_ffmpeg.concat.return_value = mock_node
    mock_ffmpeg.filter.return_value = mock_node

    mock_out = MagicMock()
    mock_ffmpeg.output.return_value = mock_out
    mock_ffmpeg.overwrite_output.return_value = mock_out

    compile_video(config, "test_out_style.mp4")

    sub_filter_calls = [
        call
        for call in mock_node.filter.mock_calls
        if call.args and call.args[0] == "subtitles"
    ]
    assert len(sub_filter_calls) > 0
    style = sub_filter_calls[0].kwargs.get("force_style", "")
    assert "FontName=Arial" in style
    assert "Shadow=2" in style


@patch("src.audio_engine.edge_tts.Communicate")
@patch("src.audio_engine.edge_tts.SubMaker")
@patch("builtins.open", new_callable=MagicMock)
def test_generate_voiceover_sync(mock_open, mock_submaker, mock_communicate):
    mock_comm_instance = MagicMock()

    # Mock the async generator for stream() using an async wrapper
    async def mock_stream():
        yield {"type": "audio", "data": b"fake_audio_data"}
        yield {"type": "WordBoundary", "data": "fake_boundary"}

    mock_comm_instance.stream.return_value = mock_stream()
    mock_communicate.return_value = mock_comm_instance

    mock_sub_instance = MagicMock()
    mock_sub_instance.get_srt.return_value = "1\n00:00:00,000 --> 00:00:01,000\nTest"
    mock_submaker.return_value = mock_sub_instance

    from src.audio_engine import generate_voiceover

    with patch("src.audio_engine.os.makedirs"):
        generate_voiceover("Test text", "fake_output.mp3")

    # Verify file writes occurred
    assert mock_open.call_count == 2  # One for mp3, one for srt
    mock_sub_instance.feed.assert_called_once()


@patch("src.audio_engine.edge_tts.Communicate")
@patch("src.audio_engine.edge_tts.SubMaker")
@patch("builtins.open", new_callable=MagicMock)
def test_generate_voiceover_word_boundary_prioritization(
    mock_open, mock_submaker, mock_communicate
):
    mock_comm_instance = MagicMock()

    # Simulate both WordBoundary and SentenceBoundary chunks in the stream
    async def mock_stream():
        yield {"type": "audio", "data": b"fake_audio"}
        yield {"type": "SentenceBoundary", "data": "sentence_chunk"}
        yield {"type": "WordBoundary", "data": "word_chunk_1"}
        yield {"type": "WordBoundary", "data": "word_chunk_2"}

    mock_comm_instance.stream.return_value = mock_stream()
    mock_communicate.return_value = mock_comm_instance

    mock_sub_instance = MagicMock()
    mock_sub_instance.get_srt.return_value = "1\n00:00:00,000 --> 00:00:02,000\nSub"
    mock_submaker.return_value = mock_sub_instance

    from src.audio_engine import generate_voiceover

    with patch("src.audio_engine.os.makedirs"):
        generate_voiceover("Word boundary priority test", "priority.mp3")

    # When WordBoundary is present, sub_maker.feed should only receive the 2 WordBoundary chunks,
    # NOT the sentence boundary (preventing duplicate overlapping cues)
    assert mock_sub_instance.feed.call_count == 2
    fed_types = [call.args[0]["type"] for call in mock_sub_instance.feed.mock_calls]
    assert all(t == "WordBoundary" for t in fed_types)


@patch("src.audio_engine.edge_tts.Communicate")
@patch("src.audio_engine.edge_tts.SubMaker")
@patch("builtins.open", new_callable=MagicMock)
def test_generate_voiceover_fallback_subtitle(
    mock_open, mock_submaker, mock_communicate
):
    mock_comm_instance = MagicMock()

    async def mock_stream():
        yield {"type": "audio", "data": b"fake_audio_data"}

    mock_comm_instance.stream.return_value = mock_stream()
    mock_communicate.return_value = mock_comm_instance

    # Mock empty string from SubMaker
    mock_sub_instance = MagicMock()
    mock_sub_instance.get_srt.return_value = ""
    mock_submaker.return_value = mock_sub_instance

    from src.audio_engine import generate_voiceover

    with patch("src.audio_engine.os.makedirs"):
        generate_voiceover("Test fallback text", "fake_output.mp3")

    # Ensure write was called with fallback content containing the text
    handle = mock_open.return_value.__enter__.return_value
    write_calls = [call.args[0] for call in handle.write.mock_calls if call.args]
    assert any("Test fallback text" in str(arg) for arg in write_calls)
    assert any("00:00:00,000 --> 00:00:" in str(arg) for arg in write_calls)


def test_format_subtitle_cues_wrapping():
    long_cue_text = (
        "1\n00:00:00,000 --> 00:00:04,500\n"
        "This is an exceptionally long educational caption line that causes overflow."
    )
    wrapped = format_subtitle_cues(long_cue_text, max_line_length=35)

    lines = wrapped.strip().split("\n")
    assert lines[0] == "1"
    assert lines[1] == "00:00:00,000 --> 00:00:04,500"
    # Verify text was broken into multiple wrapped lines
    assert len(lines) > 3
    for line in lines[2:]:
        assert len(line) <= 35


def test_audio_engine_minimum_cue_duration():
    short_cue = "1\n00:00:01,000 --> 00:00:01,300\nQuick word"
    formatted = format_subtitle_cues(short_cue, min_duration=1.2)
    assert "00:00:01,000 --> 00:00:02,200" in formatted


def test_format_subtitle_cues_chronological_sorting_and_overlap_deduplication():
    # Provide cues out of order with overlapping timestamps
    out_of_order_cues = (
        "2\n00:00:03,000 --> 00:00:05,000\nSecond cue occurring later.\n\n"
        "1\n00:00:01,000 --> 00:00:03,500\nFirst cue overlapping with second.\n\n"
        "3\n00:00:04,500 --> 00:00:06,000\nThird cue overlapping with second."
    )
    formatted = format_subtitle_cues(out_of_order_cues, min_duration=1.0)
    blocks = [b.strip() for b in formatted.strip().split("\n\n") if b.strip()]

    assert len(blocks) == 3
    # Check numbering is resequenced 1, 2, 3
    assert blocks[0].startswith("1\n00:00:01,000 --> 00:00:02,950")
    assert "First cue overlapping" in blocks[0]

    assert blocks[1].startswith("2\n00:00:03,000 --> 00:00:04,450")
    assert "Second cue occurring later" in blocks[1]

    assert blocks[2].startswith("3\n00:00:04,500 --> 00:00:06,000")
    assert "Third cue overlapping with second" in blocks[2]


def test_format_subtitle_cues_clean_whitespace_and_word_boundaries():
    cue_with_messy_whitespace = (
        "1\n00:00:00,000 --> 00:00:02,000\n"
        "  Intracellular   metabolic   pathways  function   continuously.  "
    )
    formatted = format_subtitle_cues(cue_with_messy_whitespace, max_line_length=35)
    assert "  " not in formatted
    assert "Intracellular metabolic pathways" in formatted
