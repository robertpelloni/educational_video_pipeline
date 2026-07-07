import pytest
import jsonschema
from src.config import load_config, SCHEMA
import os


def test_schema_valid_config():
    valid_config = {
        "project_id": "test_001",
        "canvas_format": "landscape",
        "background_music": "assets/music/bg.mp3",
        "global_music_volume_db": -18.0,
        "scenes": [
            {
                "sequence": 1,
                "text": "test scene",
                "image_path": "assets/images/1.png",
                "voiceover_path": "assets/audio/1.mp3",
                "choices": [
                    {"label": "Next", "target_sequence": 2}
                ]
            }
        ],
        "platforms": ["youtube"],
        "youtube_metadata": {
            "title": "Title",
            "description": "Desc",
            "tags": ["tag"],
            "category_id": "27",
        },
    }
    jsonschema.validate(instance=valid_config, schema=SCHEMA)


def test_schema_missing_required_fields():
    invalid_config = {
        "project_id": "test_001",
        # missing canvas_format
        "background_music": "assets/music/bg.mp3",
        "global_music_volume_db": -18.0,
        "scenes": [],
        "youtube_metadata": {},
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=invalid_config, schema=SCHEMA)


def test_schema_invalid_choice_format():
    invalid_config = {
        "project_id": "test_001",
        "canvas_format": "landscape",
        "background_music": "assets/music/bg.mp3",
        "global_music_volume_db": -18.0,
        "scenes": [
            {
                "sequence": 1,
                "text": "test scene",
                "image_path": "assets/images/1.png",
                "voiceover_path": "assets/audio/1.mp3",
                "choices": [
                    {"label": "Next"} # Missing target_sequence
                ]
            }
        ],
        "platforms": ["youtube"],
        "youtube_metadata": {
            "title": "Title",
            "description": "Desc",
            "tags": ["tag"],
            "category_id": "27",
        },
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=invalid_config, schema=SCHEMA)
