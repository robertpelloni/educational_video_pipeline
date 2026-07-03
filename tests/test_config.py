import pytest
import json
import os
import jsonschema
from src.config import load_config, SCHEMA

def test_valid_config(tmp_path):
    valid_data = {
        "project_id": "edu_anatomy_heart_001",
        "canvas_format": "landscape",
        "background_music": "assets/music/psytrance_track.mp3",
        "global_music_volume_db": -18.0,
        "scenes": [
            {
                "sequence": 1,
                "text": "The human heart beats...",
                "image_path": "assets/images/scene_1.png",
                "voiceover_path": "assets/audio/scene_1.mp3"
            }
        ],
        "youtube_metadata": {
            "title": "Heart",
            "description": "Desc",
            "tags": ["sci"],
            "category_id": "27"
        }
    }

    file_path = tmp_path / "config.json"
    with open(file_path, "w") as f:
        json.dump(valid_data, f)

    config = load_config(file_path)
    assert config["project_id"] == "edu_anatomy_heart_001"

def test_missing_required_field(tmp_path):
    invalid_data = {
        "project_id": "edu_anatomy_heart_001",
        # missing scenes
        "canvas_format": "landscape",
        "background_music": "assets/music/psytrance_track.mp3",
        "global_music_volume_db": -18.0,
        "youtube_metadata": {
            "title": "Heart",
            "description": "Desc",
            "tags": ["sci"],
            "category_id": "27"
        }
    }

    file_path = tmp_path / "config.json"
    with open(file_path, "w") as f:
        json.dump(invalid_data, f)

    with pytest.raises(jsonschema.ValidationError):
        load_config(file_path)
