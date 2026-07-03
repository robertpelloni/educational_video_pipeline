import pytest
import jsonschema
from src.llm_engine import generate_script_from_text
from src.config import SCHEMA

def test_generate_script_schema_validation():
    # Provide a simple multi-sentence text
    raw_text = "This is the first test sentence. This is the second test sentence."

    # Generate the script dictionary
    result = generate_script_from_text(raw_text, project_id="test_001")

    # Verify the structure perfectly matches the application schema
    try:
        jsonschema.validate(instance=result, schema=SCHEMA)
    except jsonschema.ValidationError as e:
        pytest.fail(f"LLM Engine output did not match required schema: {e}")

    # Verify logic parses sentences properly
    assert result["project_id"] == "test_001"
    assert len(result["scenes"]) == 2
    assert result["scenes"][0]["text"] == "This is the first test sentence."

def test_generate_script_empty_text():
    # Verify it handles empty input correctly
    with pytest.raises(ValueError, match="Cannot generate script from empty text."):
        generate_script_from_text("")
