import pytest
import jsonschema
import json
from src.config import load_config, SCHEMA


def test_schema_valid_config():
    valid_config = {
        "project_id": "test_001",
        "canvas_format": "landscape",
        "background_music": "",
        "global_music_volume_db": -18.0,
        "scenes": [
            {
                "sequence": 1,
                "text": "test scene",
                "image_path": "assets/images/1.png",
                "voiceover_path": "assets/audio/1.mp3",
                "choices": [{"label": "Next", "target_sequence": 2}],
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
        "background_music": "",
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
        "background_music": "",
        "global_music_volume_db": -18.0,
        "scenes": [
            {
                "sequence": 1,
                "text": "test scene",
                "image_path": "assets/images/1.png",
                "voiceover_path": "assets/audio/1.mp3",
                "choices": [{"label": "Next"}],  # Missing target_sequence
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


def test_load_config_invalid_json(tmp_path):
    invalid_json_file = tmp_path / "invalid.json"
    invalid_json_file.write_text("{ this is not valid json")

    with pytest.raises(json.JSONDecodeError):
        load_config(str(invalid_json_file))


def test_load_config_schema_validation_error(tmp_path):
    invalid_config = {
        "project_id": "test_001",
        "background_music": "",
        "global_music_volume_db": -18.0,
        "scenes": [],
        "youtube_metadata": {},
    }

    config_file = tmp_path / "invalid_schema.json"
    config_file.write_text(json.dumps(invalid_config))

    with pytest.raises(jsonschema.ValidationError):
        load_config(str(config_file))


def test_load_config_missing_image_asset(tmp_path):
    # Valid schema, but file will not exist
    config_data = {
        "project_id": "test_001",
        "canvas_format": "landscape",
        "background_music": "",
        "global_music_volume_db": -18.0,
        "scenes": [
            {
                "sequence": 1,
                "text": "test scene",
                "image_path": "non_existent_image.png",
                "voiceover_path": "assets/audio/1.mp3",
            }
        ],
        "youtube_metadata": {
            "title": "Title",
            "description": "Desc",
            "tags": ["tag"],
            "category_id": "27",
        },
    }

    config_file = tmp_path / "valid_schema_missing_asset.json"
    config_file.write_text(json.dumps(config_data))

    with pytest.raises(
        FileNotFoundError, match="Configuration error: Source image asset not found"
    ):
        load_config(str(config_file))


def test_load_config_missing_voiceover_asset(tmp_path):
    config_data = {
        "project_id": "test_001",
        "canvas_format": "landscape",
        "background_music": "",
        "global_music_volume_db": -18.0,
        "scenes": [
            {
                "sequence": 1,
                "text": "test scene",
                "image_path": "valid_image.png",
                "voiceover_path": "non_existent_audio.mp3",
            }
        ],
        "youtube_metadata": {
            "title": "Title",
            "description": "Desc",
            "tags": ["tag"],
            "category_id": "27",
        },
    }

    # Touch the image path so it passes the first check
    img_path = tmp_path / "valid_image.png"
    img_path.touch()

    config_file = tmp_path / "valid_schema_missing_audio.json"
    config_file.write_text(json.dumps(config_data))

    with pytest.raises(
        FileNotFoundError, match="Configuration error: Source voiceover asset not found"
    ):
        load_config(str(config_file))


def test_load_config_missing_background_music(tmp_path):
    config_data = {
        "project_id": "test_001",
        "canvas_format": "landscape",
        "background_music": "non_existent_bg.mp3",
        "global_music_volume_db": -18.0,
        "scenes": [
            {
                "sequence": 1,
                "text": "test scene",
                "image_path": "valid_image.png",
                "voiceover_path": "valid_audio.mp3",
            }
        ],
        "youtube_metadata": {
            "title": "Title",
            "description": "Desc",
            "tags": ["tag"],
            "category_id": "27",
        },
    }

    img_path = tmp_path / "valid_image.png"
    img_path.touch()

    audio_path = tmp_path / "valid_audio.mp3"
    audio_path.touch()

    config_file = tmp_path / "valid_schema_missing_music.json"
    config_file.write_text(json.dumps(config_data))

    with pytest.raises(
        FileNotFoundError, match="Configuration error: Background music asset not found"
    ):
        load_config(str(config_file))
