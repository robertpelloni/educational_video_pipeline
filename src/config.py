import json
import jsonschema

SCHEMA = {
    "type": "object",
    "properties": {
        "project_id": {"type": "string"},
        "canvas_format": {"type": "string", "enum": ["landscape", "portrait"]},
        "background_music": {"type": "string"},
        "global_music_volume_db": {"type": "number"},
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "sequence": {"type": "integer"},
                    "text": {"type": "string"},
                    "image_path": {"type": "string"},
                    "voiceover_path": {"type": "string"}
                },
                "required": ["sequence", "text", "image_path", "voiceover_path"]
            }
        },
        "youtube_metadata": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "tags": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "category_id": {"type": "string"}
            },
            "required": ["title", "description", "tags", "category_id"]
        }
    },
    "required": ["project_id", "canvas_format", "background_music", "global_music_volume_db", "scenes", "youtube_metadata"]
}

def load_config(file_path):
    """
    Loads and validates a job execution schema configuration file.

    Args:
        file_path (str): The path to the configuration JSON file.

    Returns:
        dict: The parsed and validated configuration.

    Raises:
        json.JSONDecodeError: If the file is not valid JSON.
        jsonschema.ValidationError: If the JSON does not conform to the expected schema.
        FileNotFoundError: If the file does not exist.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    jsonschema.validate(instance=config, schema=SCHEMA)
    return config
