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
    color_palette: Optional[str] = Field(
        default="balanced scientific educational hues with high-contrast accents",
        description="Cohesive color grading palette (e.g. vibrant indigo, golden amber, deep neutral slate).",
    )
    artistic_medium: Optional[str] = Field(
        default="digital vector illustration",
        description="Visual execution medium (e.g. 3D volumetric render, digital vector, photography).",
    )
    focal_point: Optional[str] = Field(
        default="center",
        description="Primary focal anchor point within the canvas (e.g. 'center', 'top', 'bottom', 'left', 'right').",
    )
    pacing_tempo: Optional[str] = Field(
        default="exposition",
        description=(
            "Narrative pacing role: 'hook_intro', 'exposition', 'deep_dive', "
            "'dramatic_revelation', or 'summary_call_to_action'."
        ),
    )
    voice_tone: Optional[str] = Field(
        default="calm_educational",
        description="Narration tone: 'authoritative_documentary', 'enthusiastic_explainer', 'calm_educational'.",
    )
    depth_of_field: Optional[str] = Field(
        default="subtle depth of field with sharp central focal plane",
        description="Optical depth characteristics (e.g. 'shallow bokeh', 'deep universal focus').",
    )
    atmospheric_mood: Optional[str] = Field(
        default="clean pristine studio clarity",
        description="Environmental atmospheric mood (e.g. 'subtle volumetric haze', 'pristine studio clarity').",
    )
    audience_reading_level: Optional[
        Literal["elementary", "general_public", "academic_specialist"]
    ] = Field(
        default="general_public",
        description="Target educational vocabulary and complexity level.",
    )
    emphasis_keywords: Optional[List[str]] = Field(
        default_factory=list,
        description="Key conceptual tokens to stress in audio TTS and highlight in subtitles.",
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
    color_palette: Optional[str] = Field(
        default="balanced scientific educational hues with high-contrast accents",
        description="Global color grading palette applied across the video.",
    )
    artistic_medium: Optional[str] = Field(
        default="digital vector illustration",
        description="Global artistic medium applied across the video.",
    )
    audience_reading_level: Optional[
        Literal["elementary", "general_public", "academic_specialist"]
    ] = Field(
        default="general_public",
        description="Global audience reading difficulty level.",
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


def extract_key_visual_entities(text: str, max_entities: int = 5) -> List[str]:
    """
    Heuristically extracts key tangible nouns and scientific entities from narration text
    to anchor visual prompt consistency and avoid generic abstractions.
    """
    stop_words = {
        "this",
        "that",
        "these",
        "those",
        "there",
        "their",
        "which",
        "where",
        "when",
        "what",
        "then",
        "with",
        "from",
        "into",
        "during",
        "including",
        "until",
        "against",
        "among",
        "throughout",
        "despite",
        "towards",
        "upon",
        "concerning",
        "about",
        "also",
        "very",
        "often",
        "many",
        "some",
        "such",
        "other",
        "captures",
        "observations",
        "generate",
        "bends",
    }
    import re

    # Find prominent words (> 3 chars)
    words = re.findall(r"\b[A-Za-z0-9_-]{4,}\b", text)
    entities = [w for w in words if w.lower() not in stop_words]
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for e in entities:
        if e.lower() not in seen:
            seen.add(e.lower())
            deduped.append(e)
    return deduped[:max_entities]


def validate_visual_prompt_quality(prompt: str) -> dict:
    """
    Evaluates visual prompt quality score (0.0 - 1.0) based on specificity,
    presence of framing directives, illumination cues, and tangible subject nouns.
    """
    if not prompt or len(prompt.strip()) == 0:
        return {"score": 0.0, "is_valid": False, "missing": ["content"]}

    missing = []
    p_lower = prompt.lower()

    if not any(
        k in p_lower for k in ["framing:", "shot", "view", "close-up", "establishing"]
    ):
        missing.append("framing")

    if not any(
        k in p_lower for k in ["lighting:", "illumination", "light", "rim", "ambient"]
    ):
        missing.append("lighting")

    if not any(
        k in p_lower
        for k in ["style:", "illustration", "cinematography", "render", "engraving"]
    ):
        missing.append("style")

    word_count = len(prompt.split())
    if word_count < 8:
        missing.append("detail_depth")

    score = max(0.2, (4 - len(missing)) / 4.0)
    return {
        "score": score,
        "is_valid": score >= 0.5,
        "missing": missing,
        "word_count": word_count,
    }


def compose_scene_visual_prompt(
    scene: dict,
    global_style_anchor: Optional[str] = None,
    include_negatives: bool = False,
    max_words: int = 300,
    canvas_format: Optional[str] = None,
) -> str:
    """
    Synthesizes a cohesive, composite visual prompt for image generation,
    combining scene description, camera angle, lighting setup, and style anchors
    without redundant repetition.
    """
    parts = []

    def clean_token(val: str) -> str:
        v = val.strip()
        v = v.rstrip(".,; ")
        return v

    visual_prompt = (
        scene.get("visual_prompt")
        or f"Educational illustration regarding: {scene.get('text', '')}"
    )
    parts.append(clean_token(visual_prompt))

    # Weave tangible focal subject entity if specified
    focal_subject = scene.get("focal_subject")
    if focal_subject and focal_subject not in visual_prompt:
        parts.append(f"Primary focal subject: {clean_token(focal_subject)}")

    camera_angle = scene.get("camera_angle")
    if camera_angle and camera_angle not in visual_prompt:
        parts.append(f"Framing: {clean_token(camera_angle)}")

    # Add canvas format spatial framing directive if provided
    fmt = canvas_format or scene.get("canvas_format")
    if fmt == "portrait":
        parts.append("Spatial layout: 9:16 vertical composition, centered subject")
    elif fmt == "landscape":
        parts.append("Spatial layout: 16:9 widescreen composition, expansive view")

    lighting = scene.get("lighting_setup")
    if lighting and lighting not in visual_prompt:
        parts.append(f"Lighting: {clean_token(lighting)}")

    palette = scene.get("color_palette")
    if palette and palette not in visual_prompt:
        parts.append(f"Palette: {clean_token(palette)}")

    dof = scene.get("depth_of_field")
    if dof and dof not in visual_prompt:
        parts.append(f"Optics: {clean_token(dof)}")

    mood = scene.get("atmospheric_mood")
    if mood and mood not in visual_prompt:
        parts.append(f"Atmosphere: {clean_token(mood)}")

    medium = scene.get("artistic_medium")
    if medium and medium not in visual_prompt:
        parts.append(f"Medium: {clean_token(medium)}")

    style = scene.get("visual_style_anchor") or global_style_anchor
    if style and style not in visual_prompt:
        parts.append(f"Style: {clean_token(style)}")

    res = ". ".join(p for p in parts if p)
    # Normalize excessive spaces and sanitize redundant punctuation
    import re

    res = re.sub(r"\s+", " ", res).strip()
    res = re.sub(r"\s+([.,])", r"\1", res)
    res = re.sub(r"\.{2,}", ".", res)

    if not res.endswith("."):
        res += "."

    if include_negatives:
        neg = scene.get("negative_prompt") or DEFAULT_NEGATIVE_PROMPT
        if neg:
            res += f" Avoid: {neg.strip()}."

    # Enforce optimal token length bound for image generator APIs
    words = res.split()
    if len(words) > max_words:
        res = " ".join(words[:max_words]).rstrip(".") + "."

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
            "To maximize visual continuity and relevance: "
            f"1. Enforce this cohesive visual_style_anchor across all scenes: '{chosen_style_anchor}'. "
            "2. Maintain strict subject identity and visual continuity across scenes referencing the topic entity. "
            "3. Ground each scene's 'visual_prompt' in concrete, tangible physical objects, mechanisms, "
            "and physical environments described in the narration. "
            "Explicitly avoid generic or vague abstract metaphors. "
            "4. For each scene, craft a 'visual_prompt' specifying camera framing (wide establishing shot, "
            "macro focal view, or cross-section cutaway), dynamic studio lighting, and clear subject isolation. "
            "5. Enforce the identical visual_style_anchor on every scene to guarantee stylistic harmony. "
            "6. Provide targeted 'negative_prompt' tokens to suppress text artifacts, watermarks, and blurry renders."
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

    pacing_sequence = [
        "hook_intro",
        "exposition",
        "deep_dive",
        "dramatic_revelation",
        "summary_call_to_action",
    ]

    scenes = []
    subject_entity = project_id.replace("_", " ").title()
    prev_focal_elements = []

    for index, sentence in enumerate(sentences, start=1):
        clean_sentence = sentence.rstrip(".")
        framing = framing_sequence[(index - 1) % len(framing_sequence)]
        pacing = pacing_sequence[min(index - 1, len(pacing_sequence) - 1)]
        lighting = "volumetric studio rim lighting with soft ambient fill"
        palette = "balanced scientific educational hues with high-contrast accents"
        medium = "digital vector illustration"

        # Ground scene prompt in concrete semantic entities extracted from narration
        entities = extract_key_visual_entities(clean_sentence)
        entity_grounding = (
            f" Concrete elements: {', '.join(entities)}." if entities else ""
        )

        transition_context = ""
        if prev_focal_elements:
            transition_context = (
                f" Visual continuity from: {', '.join(prev_focal_elements[:2])}."
            )
        if entities:
            prev_focal_elements = entities

        prompt_str = (
            f"{framing} depicting: {clean_sentence}. Consistent focal subject: {subject_entity}."
            f"{entity_grounding}{transition_context} Illumination: {lighting}. Palette: {palette}. Medium: {medium}. "
            f"Narrative pacing: {pacing}. Balanced exposure, high-contrast clarity, and uncluttered background"
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
                "color_palette": palette,
                "artistic_medium": medium,
                "pacing_tempo": pacing,
                "voice_tone": (
                    "calm_educational" if index > 1 else "enthusiastic_explainer"
                ),
                "emphasis_keywords": entities[:3] if entities else [],
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
        "color_palette": "balanced scientific educational hues with high-contrast accents",
        "artistic_medium": "digital vector illustration",
        "platforms": ["youtube", "tiktok", "instagram", "twitter"],
        "scenes": scenes,
        "youtube_metadata": {
            "title": f"Automated Educational Video: {project_id}",
            "description": "Generated autonomously from public domain text.",
            "tags": ["education", "automated", "science"],
            "category_id": "27",
        },
    }
