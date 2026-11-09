import logging
import os
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Literal, Union, Optional

logger = logging.getLogger(__name__)


# Pydantic Models for Instructor
class BranchChoice(BaseModel):
    label: str = Field(
        description="The text displayed on the interactive button for the user to choose."
    )
    target_sequence: int = Field(
        description="The sequence ID of the scene to jump to if this choice is selected."
    )


class Quiz(BaseModel):
    question: str = Field(description="The question to ask the user.")
    options: List[str] = Field(description="A list of possible answers for the quiz.")
    correct_answer_index: int = Field(
        description="The zero-based index of the correct answer in the options list."
    )


DEFAULT_STYLE_ANCHOR = (
    "hyper-detailed scientific educational digital illustration, crisp vector-like clean lines, "
    "cinematic studio volumetric lighting, deep rich educational color palette, 8k resolution, "
    "centered focal composition, clean modern textbook aesthetics"
)

DEFAULT_NEGATIVE_PROMPT = (
    "text, watermark, logo, typography, blurry, fuzzy, oversaturated, deformed, disfigured, "
    "mutated, extra limbs, poor anatomy, low quality, artifacts, noisy background"
)

STYLE_PRESETS = {
    "scientific_schematic": DEFAULT_STYLE_ANCHOR,
    "cinematic_documentary": (
        "photorealistic BBC nature documentary cinematography, 35mm anamorphic lens, "
        "natural golden hour rim lighting, shallow depth of field, authentic film grain, "
        "hyper-detailed realistic textures, cinematic color grade"
    ),
    "historical_engraving": (
        "classical 19th-century vintage copperplate engraving, intricate cross-hatching, "
        "antique parchment texture, sepia monochrome palette, museum archival quality, "
        "refined botanical and technical draftsmanship"
    ),
    "microscopic_render": (
        "fluorescence confocal electron microscope scan, false-color luminescent emission, "
        "extreme optical magnification, deep black background, volumetric glow, "
        "sub-cellular structural clarity"
    ),
}


class Scene(BaseModel):
    sequence: int
    text: str = Field(description="The educational narration for this specific scene.")
    visual_prompt: Optional[str] = Field(
        default=None,
        description=(
            "Detailed descriptive prompt for generating visual scene assets. "
            "Describe the subject in explicit action, framing, and environment, tightly aligned "
            "with the educational narration, without repeating general style anchors."
        ),
    )
    visual_style_anchor: Optional[str] = Field(
        default=DEFAULT_STYLE_ANCHOR,
        description=(
            "Cohesive visual style anchor shared across all scenes in this project "
            "(e.g., artistic medium, color palette, lighting treatment, aesthetic texture)."
        ),
    )
    negative_prompt: Optional[str] = Field(
        default=DEFAULT_NEGATIVE_PROMPT,
        description="Negative prompt tokens to suppress text, watermarks, deformities, and artifacts.",
    )
    lighting_setup: Optional[str] = Field(
        default="volumetric studio rim lighting with soft ambient fill",
        description="Explicit lighting setup to guarantee illumination continuity across scene transitions.",
    )
    camera_angle: Optional[str] = Field(
        default="eye-level centered macro framing",
        description="Camera perspective or shot angle (e.g. eye-level, low-angle, top-down schematic, cutaway).",
    )
    image_path: str = Field(
        description="Path to save the generated image. Use 'assets/images/{project_id}_scene_{sequence}.png'"
    )
    voiceover_path: str = Field(
        description="Path to save the generated audio. Use 'assets/audio/{project_id}_scene_{sequence}.mp3'"
    )
    quiz: Optional[Quiz] = Field(
        default=None,
        description="Optional mid-stream quiz to present to the user at the end of the scene.",
    )
    choices: Optional[List[BranchChoice]] = Field(
        default=None,
        description="Optional list of interactive branching choices for this scene.",
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
    visual_style_anchor: Optional[str] = Field(
        default=DEFAULT_STYLE_ANCHOR,
        description="Global unified visual style anchor enforced across all scenes.",
    )
    negative_prompt: Optional[str] = Field(
        default=DEFAULT_NEGATIVE_PROMPT,
        description="Global negative prompt tokens for image synthesis.",
    )
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


def compose_scene_visual_prompt(
    scene: dict,
    global_style_anchor: Optional[str] = None,
    include_negatives: bool = False,
) -> str:
    """
    Synthesizes a cohesive, composite visual prompt for image generation,
    combining scene description, camera angle, lighting setup, and style anchors
    without redundant repetition.
    """
    parts = []

    visual_prompt = (
        scene.get("visual_prompt")
        or f"Educational illustration regarding: {scene.get('text', '')}"
    )
    parts.append(visual_prompt.rstrip("."))

    camera_angle = scene.get("camera_angle")
    if camera_angle and camera_angle not in visual_prompt:
        parts.append(f"Framing: {camera_angle}")

    lighting = scene.get("lighting_setup")
    if lighting and lighting not in visual_prompt:
        parts.append(f"Lighting: {lighting}")

    style = scene.get("visual_style_anchor") or global_style_anchor
    if style and style not in visual_prompt:
        parts.append(f"Style: {style}")

    res = ". ".join(parts)
    if not res.endswith("."):
        res += "."

    if include_negatives:
        neg = scene.get("negative_prompt") or DEFAULT_NEGATIVE_PROMPT
        if neg:
            res += f" Avoid: {neg}."

    return res


def generate_script_from_text(
    raw_text: str,
    project_id: str = "auto_gen_001",
    analytics_feedback: str = None,
    style_preset: Optional[str] = None,
) -> dict:
    """
    Generates a structured video script adhering to the pipeline schema using OpenAI and Instructor.
    Falls back to a naive parsing mock if OPENAI_API_KEY is not present.
    """
    if not raw_text or len(raw_text.strip()) == 0:
        logger.error("Raw text input to LLM engine is empty.")
        raise ValueError("Cannot generate script from empty text.")

    logger.info(f"Generating LLM script for project {project_id}...")

    chosen_style_anchor = STYLE_PRESETS.get(style_preset, DEFAULT_STYLE_ANCHOR)

    client = get_llm_client()

    if client:
        # Real LLM Execution via Instructor
        system_prompt = (
            "You are an expert educational video scriptwriter and visual art director. "
            "Your task is to parse educational content into a visually coherent sequence of scenes. "
            "To maximize visual continuity: "
            f"1. Enforce this cohesive visual_style_anchor across all scenes: '{chosen_style_anchor}'. "
            "2. Maintain strict subject identity and visual continuity across scenes referencing the topic entity. "
            "3. For each scene, craft a 'visual_prompt' specifying camera framing (wide establishing shot, "
            "macro focal view, or cross-section cutaway), dynamic studio lighting, and clear subject isolation. "
            "4. Enforce the identical visual_style_anchor on every scene to guarantee stylistic harmony. "
            "5. Provide targeted 'negative_prompt' tokens to suppress text artifacts, watermarks, and blurry renders."
        )
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
            script_dict = script.model_dump()
            # If user explicitly specified style_preset, ensure anchor is assigned
            if style_preset:
                script_dict["visual_style_anchor"] = chosen_style_anchor
                for sc in script_dict.get("scenes", []):
                    sc["visual_style_anchor"] = chosen_style_anchor
            return script_dict
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

    framing_sequence = [
        "Wide establishing shot, centered focal subject with clean isolation",
        "Medium macro focus on key mechanism, volumetric studio side-lighting",
        "Detailed cutaway diagram cross-section, crisp edge definition and clarity",
        "Cinematic low-angle educational view, subtle depth of field and soft rim light",
    ]

    scenes = []
    subject_entity = project_id.replace("_", " ").title()

    for index, sentence in enumerate(sentences, start=1):
        clean_sentence = sentence.rstrip(".")
        framing = framing_sequence[(index - 1) % len(framing_sequence)]
        lighting = "volumetric studio rim lighting with soft ambient fill"
        prompt_str = (
            f"{framing} depicting: {clean_sentence}. Consistent focal subject: {subject_entity}. "
            f"Illumination: {lighting}. Balanced exposure, high-contrast clarity, and uncluttered background"
        )
        scenes.append(
            {
                "sequence": index,
                "text": sentence,
                "visual_prompt": prompt_str,
                "visual_style_anchor": chosen_style_anchor,
                "negative_prompt": DEFAULT_NEGATIVE_PROMPT,
                "lighting_setup": lighting,
                "camera_angle": framing,
                "image_path": f"assets/images/{project_id}_scene_{index}.png",
                "voiceover_path": f"assets/audio/{project_id}_scene_{index}.mp3",
            }
        )

    return {
        "project_id": project_id,
        "canvas_format": ["landscape", "portrait"],
        "background_music": "assets/music/default_background.mp3",
        "global_music_volume_db": -18.0,
        "visual_style_anchor": chosen_style_anchor,
        "negative_prompt": DEFAULT_NEGATIVE_PROMPT,
        "platforms": ["youtube", "tiktok", "instagram", "twitter"],
        "scenes": scenes,
        "youtube_metadata": {
            "title": f"Automated Educational Video: {project_id}",
            "description": "Generated autonomously from public domain text.",
            "tags": ["education", "automated", "science"],
            "category_id": "27",
        },
    }
