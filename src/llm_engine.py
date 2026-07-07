import logging
import os
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Literal, Union, Optional

logger = logging.getLogger(__name__)


# Pydantic Models for Instructor
class BranchChoice(BaseModel):
    label: str = Field(description="The text displayed on the interactive button for the user to choose.")
    target_sequence: int = Field(description="The sequence ID of the scene to jump to if this choice is selected.")


class Scene(BaseModel):
    sequence: int
    text: str = Field(description="The educational narration for this specific scene.")
    image_path: str = Field(
        description="The relative path to save the generated image. Use the format 'assets/images/{project_id}_scene_{sequence}.png'"
    )
    voiceover_path: str = Field(
        description="The relative path to save the generated audio. Use the format 'assets/audio/{project_id}_scene_{sequence}.mp3'"
    )
    choices: Optional[List[BranchChoice]] = Field(
        default=None,
        description="Optional list of interactive branching choices presented at the end of this scene for web-player playback."
    )


class YouTubeMetadata(BaseModel):
    title: str = Field(description="An engaging title for the video.")
    description: str = Field(
        description="A detailed description for the video, suitable for YouTube or TikTok."
    )
    tags: List[str] = Field(description="A list of 3-5 relevant hashtags.")
    category_id: str = Field(
        default="27", description="The YouTube category ID, defaults to 27 (Education)."
    )


class VideoScript(BaseModel):
    project_id: str
    canvas_format: Union[
        Literal["landscape", "portrait"], List[Literal["landscape", "portrait"]]
    ] = Field(default=["landscape", "portrait"])
    background_music: str = Field(default="assets/music/default_background.mp3")
    global_music_volume_db: float = Field(default=-18.0)
    platforms: List[Literal["youtube", "tiktok", "instagram", "twitter"]] = Field(
        default=["youtube", "tiktok", "instagram", "twitter"]
    )
    scenes: List[Scene]
    youtube_metadata: YouTubeMetadata


# Initialize the OpenAI client wrapped with Instructor
# We will gracefully fall back to a mock generation if the API key is missing to prevent breaking local dev
def get_llm_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return instructor.from_openai(OpenAI(api_key=api_key))


def generate_script_from_text(
    raw_text: str, project_id: str = "auto_gen_001", analytics_feedback: str = None
) -> dict:
    """
    Generates a structured video script adhering to the pipeline schema using OpenAI and Instructor.
    Falls back to a naive parsing mock if OPENAI_API_KEY is not present.
    """
    if not raw_text or len(raw_text.strip()) == 0:
        logger.error("Raw text input to LLM engine is empty.")
        raise ValueError("Cannot generate script from empty text.")

    logger.info(f"Generating LLM script for project {project_id}...")

    client = get_llm_client()

    if client:
        # Real LLM Execution via Instructor
        system_prompt = "You are an expert educational video scriptwriter. Your job is to parse raw text and structure it into an engaging sequence of scenes for a video."
        if analytics_feedback:
            system_prompt += f" Consider this feedback from previous videos to improve engagement: {analytics_feedback}"

        try:
            logger.info("Executing OpenAI completion request via Instructor...")
            script: VideoScript = client.chat.completions.create(
                model="gpt-4o",
                response_model=VideoScript,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Project ID: {project_id}\n\nRaw Text to parse: {raw_text}",
                    },
                ],
            )
            return script.model_dump()
        except Exception as e:
            logger.error(
                f"Instructor LLM generation failed: {e}. Falling back to mock parsing."
            )
            # Fall through to mock logic on failure

    # --- Fallback Mock Logic (For local dev without API keys) ---
    logger.info("Using fallback mock script generation.")

    sentences = [s.strip() + "." for s in raw_text.split(".") if len(s.strip()) > 10]
    if not sentences:
        sentences = [raw_text[:100] + "..."]

    scenes = []
    for index, sentence in enumerate(sentences, start=1):
        scenes.append(
            {
                "sequence": index,
                "text": sentence,
                "image_path": f"assets/images/{project_id}_scene_{index}.png",
                "voiceover_path": f"assets/audio/{project_id}_scene_{index}.mp3",
            }
        )

    return {
        "project_id": project_id,
        "canvas_format": ["landscape", "portrait"],
        "background_music": "assets/music/default_background.mp3",
        "global_music_volume_db": -18.0,
        "platforms": ["youtube", "tiktok", "instagram", "twitter"],
        "scenes": scenes,
        "youtube_metadata": {
            "title": f"Automated Educational Video: {project_id}",
            "description": "Generated autonomously from public domain text.",
            "tags": ["education", "automated", "science"],
            "category_id": "27",
        },
    }
