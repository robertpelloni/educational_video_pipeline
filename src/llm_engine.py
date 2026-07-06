import logging

logger = logging.getLogger(__name__)


def generate_script_from_text(
    raw_text: str, project_id: str = "auto_gen_001", analytics_feedback: str = None
) -> dict:
    """
    Simulates an LLM endpoint that takes raw ingestion text and formats it
    into the strict JSON schema required by the pipeline's configuration engine.

    In a production environment, this function would wrap an OpenAI/Anthropic/Local LLM
    call, passing the raw_text into a prompt asking for JSON adhering to src.config.SCHEMA.

    Args:
        raw_text (str): The raw text ingested from an API (e.g., Wikipedia).
        project_id (str): A unique identifier for the generated job.
        analytics_feedback (str): Optional feedback string from the analytics engine to guide the LLM.

    Returns:
        dict: A dictionary structurally identical to the pipeline's JSON schema.
    """
    logger.info(f"Simulating LLM script generation for project {project_id}...")
    if analytics_feedback:
        logger.info(f"Applying analytics feedback loop: {analytics_feedback}")

    if not raw_text or len(raw_text.strip()) == 0:
        logger.error("Raw text input to LLM engine is empty.")
        raise ValueError("Cannot generate script from empty text.")

    # Split the raw text into logical "scenes" (mocking LLM summarization logic)
    # For this stub, we'll just split by sentences (periods)
    sentences = [s.strip() + "." for s in raw_text.split(".") if len(s.strip()) > 10]

    if not sentences:
        # Fallback if no clean sentences were found
        sentences = [raw_text[:100] + "..."]

    scenes = []
    for index, sentence in enumerate(sentences, start=1):
        # We assign dummy image/audio paths which the orchestrator will generate
        # or which the user must provide.
        scenes.append(
            {
                "sequence": index,
                "text": sentence,
                "image_path": f"assets/images/{project_id}_scene_{index}.png",
                "voiceover_path": f"assets/audio/{project_id}_scene_{index}.mp3",
            }
        )

    # Assemble the final schema dictionary
    script_config = {
        "project_id": project_id,
        "canvas_format": "landscape",
        "background_music": "assets/music/default_background.mp3",
        "global_music_volume_db": -18.0,
        "scenes": scenes,
        "youtube_metadata": {
            "title": f"Automated Educational Video: {project_id}",
            "description": "Generated autonomously from public domain text.",
            "tags": ["education", "automated", "science"],
            "category_id": "27",
        },
    }

    logger.debug("Successfully generated mock script config.")
    return script_config
