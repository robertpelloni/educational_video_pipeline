import pytest
import jsonschema
from unittest.mock import patch, MagicMock
from src.llm_engine import (
    generate_script_from_text,
    VideoScript,
    Scene,
    YouTubeMetadata,
    BranchChoice,
    Quiz,
)
from src.config import SCHEMA


@patch("src.llm_engine.get_llm_client", return_value=None)
def test_generate_script_schema_validation_fallback(mock_get_client):
    # Provide a simple multi-sentence text
    raw_text = "This is the first test sentence. This is the second test sentence."

    # Generate the script dictionary using the fallback mock
    result = generate_script_from_text(raw_text, project_id="test_001")

    # Verify the structure perfectly matches the application schema
    try:
        jsonschema.validate(instance=result, schema=SCHEMA)
    except jsonschema.ValidationError as e:
        pytest.fail(f"LLM Engine fallback output did not match required schema: {e}")

    # Verify logic parses sentences properly
    assert result["project_id"] == "test_001"
    assert len(result["scenes"]) == 2
    assert result["scenes"][0]["text"] == "This is the first test sentence."


@patch("src.llm_engine.get_llm_client")
def test_generate_script_schema_validation_instructor(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    mock_script = VideoScript(
        project_id="test_instructor_001",
        scenes=[
            Scene(
                sequence=1,
                text="Instructor mock text.",
                image_path="assets/images/1.png",
                voiceover_path="assets/audio/1.mp3",
                quiz=Quiz(
                    question="What is this?", options=["A", "B"], correct_answer_index=0
                ),
                choices=[BranchChoice(label="Go to scene 2", target_sequence=2)],
            )
        ],
        youtube_metadata=YouTubeMetadata(
            title="Title", description="Desc", tags=["tag1"]
        ),
    )

    # Mock the completions object returned by instructor
    mock_client.chat.completions.create.return_value = mock_script

    raw_text = "Instructor mock text."
    result = generate_script_from_text(raw_text, project_id="test_instructor_001")

    # Verify the structure perfectly matches the application schema
    try:
        jsonschema.validate(instance=result, schema=SCHEMA)
    except jsonschema.ValidationError as e:
        pytest.fail(f"Instructor LLM Engine output did not match required schema: {e}")

    assert result["project_id"] == "test_instructor_001"
    assert len(result["scenes"]) == 1
    assert result["scenes"][0]["text"] == "Instructor mock text."


def test_generate_script_empty_text():
    # Verify it handles empty input correctly
    with pytest.raises(ValueError, match="Cannot generate script from empty text."):
        generate_script_from_text("")


@patch("src.llm_engine.get_llm_client")
def test_generate_script_instructor_exception_fallback(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    mock_client.chat.completions.create.side_effect = Exception("OpenAI API Down")

    raw_text = "Fallback on exception."
    result = generate_script_from_text(raw_text, project_id="test_exception")

    # Should fall back gracefully to basic parsing
    assert result["project_id"] == "test_exception"
    assert len(result["scenes"]) == 1
    assert result["scenes"][0]["text"] == "Fallback on exception."
