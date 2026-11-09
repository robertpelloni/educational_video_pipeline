import pytest
import jsonschema
from unittest.mock import patch, MagicMock
from src.llm_engine import (
    generate_script_from_text,
    compose_scene_visual_prompt,
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
    assert "visual_prompt" in result["scenes"][0]


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


def test_generate_script_visual_prompt_alignment():
    raw_text = "The mitochondria is the powerhouse of the cell."
    result = generate_script_from_text(raw_text, project_id="bio_01")
    scene = result["scenes"][0]
    assert "visual_prompt" in scene
    assert "mitochondria" in scene["visual_prompt"]
    assert "Wide establishing shot" in scene["visual_prompt"]
    assert "uncluttered background" in scene["visual_prompt"]


def test_scene_visual_style_anchor_and_coherence():
    raw_text = (
        "Photosynthesis converts sunlight into chemical energy. "
        "Chloroplasts inside the plant cell capture photons of light. "
        "Glucose is then produced as an essential energy source."
    )
    result = generate_script_from_text(raw_text, project_id="plant_bio_01")

    # Global config must contain cohesive style anchor and negative prompt
    assert "visual_style_anchor" in result
    assert "negative_prompt" in result
    assert "hyper-detailed" in result["visual_style_anchor"]
    assert "watermark" in result["negative_prompt"]

    scenes = result["scenes"]
    assert len(scenes) == 3

    # Every scene must share the identical style anchor to ensure visual continuity
    for scene in scenes:
        assert scene["visual_style_anchor"] == result["visual_style_anchor"]
        assert scene["negative_prompt"] == result["negative_prompt"]
        assert "visual_prompt" in scene
        assert len(scene["visual_prompt"]) > 20


def test_style_preset_selection():
    raw_text = "The Roman Colosseum was built of concrete and sand."
    result = generate_script_from_text(
        raw_text, project_id="rome_01", style_preset="historical_engraving"
    )

    assert "historical_engraving" not in result["visual_style_anchor"]
    assert "copperplate engraving" in result["visual_style_anchor"]
    assert "cross-hatching" in result["visual_style_anchor"]

    for scene in result["scenes"]:
        assert scene["visual_style_anchor"] == result["visual_style_anchor"]


def test_camera_framing_directives_in_mock():
    raw_text = (
        "Neurons transmit electrochemical signals throughout the human body. "
        "The axon terminal releases neurotransmitters across the synaptic gap. "
        "Receptors on the dendrite bind these chemical messengers instantly. "
        "Action potentials propagate along the myelin sheath rapidly."
    )
    result = generate_script_from_text(raw_text, project_id="neuro_01")
    scenes = result["scenes"]
    assert len(scenes) == 4

    # Verify framing variations cycle properly through diverse camera scales
    assert "Wide establishing shot" in scenes[0]["visual_prompt"]
    assert "Medium macro focus" in scenes[1]["visual_prompt"]
    assert "Detailed cutaway diagram cross-section" in scenes[2]["visual_prompt"]
    assert "Cinematic low-angle educational view" in scenes[3]["visual_prompt"]


def test_visual_prompt_entity_continuity():
    raw_text = (
        "Saturn has prominent rings composed of ice and rock particles. "
        "The Cassini division is the largest gap within Saturn's ring system. "
        "Titan is the largest moon orbiting Saturn with a dense nitrogen atmosphere."
    )
    result = generate_script_from_text(raw_text, project_id="saturn_exploration")
    scenes = result["scenes"]
    assert len(scenes) == 3

    # All scenes must explicitly maintain subject entity continuity
    for scene in scenes:
        assert "Consistent focal subject: Saturn Exploration" in scene["visual_prompt"]


def test_scene_lighting_and_camera_angle_continuity():
    raw_text = (
        "Cellular respiration generates adenosine triphosphate. "
        "The electron transport chain creates a proton gradient across the inner mitochondrial membrane."
    )
    result = generate_script_from_text(raw_text, project_id="bio_respiration")
    scenes = result["scenes"]
    assert len(scenes) == 2

    for scene in scenes:
        assert "lighting_setup" in scene
        assert "camera_angle" in scene
        assert "volumetric studio rim lighting" in scene["lighting_setup"]
        assert "Illumination:" in scene["visual_prompt"]
        # Verify valid schema match
        jsonschema.validate(instance=result, schema=SCHEMA)


def test_compose_scene_visual_prompt():
    scene = {
        "text": "The heart pumps oxygenated blood.",
        "visual_prompt": "Detailed anatomical model of human heart",
        "camera_angle": "macro zoom cutaway",
        "lighting_setup": "cool volumetric medical lighting",
        "visual_style_anchor": "crisp vector digital schematic",
    }
    composite = compose_scene_visual_prompt(scene)

    assert "Detailed anatomical model of human heart" in composite
    assert "Framing: macro zoom cutaway" in composite
    assert "Lighting: cool volumetric medical lighting" in composite
    assert "Style: crisp vector digital schematic" in composite


def test_compose_scene_visual_prompt_with_negative_tokens():
    scene = {
        "text": "The solar flare erupts.",
        "visual_prompt": "Solar prominence rising from the chromosphere",
        "negative_prompt": "low resolution, text watermark, distortion",
    }
    composite = compose_scene_visual_prompt(scene, include_negatives=True)
    assert "Solar prominence rising from the chromosphere" in composite
    assert "Avoid: low resolution, text watermark, distortion." in composite


def test_compose_scene_visual_prompt_color_palette():
    scene = {
        "text": "Photosynthesis creates glucose.",
        "visual_prompt": "Chloroplast diagram",
        "color_palette": "emerald greens and vibrant cyan accents",
        "artistic_medium": "3D volumetric render",
    }
    composite = compose_scene_visual_prompt(scene)
    assert "Chloroplast diagram" in composite
    assert "Palette: emerald greens and vibrant cyan accents" in composite
    assert "Medium: 3D volumetric render" in composite


def test_scene_color_palette_schema_validation():
    raw_text = (
        "The speed of light in vacuum is approximately 299,792,458 meters per second."
    )
    result = generate_script_from_text(raw_text, project_id="physics_constants")

    assert "color_palette" in result
    assert "artistic_medium" in result
    for scene in result["scenes"]:
        assert "color_palette" in scene
        assert "artistic_medium" in scene

    # Validate against formal schema
    jsonschema.validate(instance=result, schema=SCHEMA)


def test_scene_focal_point_schema():
    scene = Scene(
        sequence=1,
        text="A telescope focuses on Jupiter.",
        image_path="assets/images/1.png",
        voiceover_path="assets/audio/1.mp3",
        focal_point="center",
    )
    dumped = scene.model_dump()
    assert dumped["focal_point"] == "center"
