import asyncio
import math
import os
import textwrap
import logging
from typing import Optional
import edge_tts

logger = logging.getLogger(__name__)


def parse_srt_timestamp(ts: str) -> float:
    """Parses an SRT timestamp (HH:MM:SS,mmm) into seconds."""
    try:
        time_part, millis_part = ts.split(",")
        hours, minutes, seconds = map(int, time_part.split(":"))
        return hours * 3600 + minutes * 60 + seconds + int(millis_part) / 1000.0
    except Exception:
        return 0.0


def format_srt_timestamp(seconds: float) -> str:
    """Formats seconds into an SRT timestamp string (HH:MM:SS,mmm)."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def format_subtitle_cues(
    srt_content: str,
    max_line_length: int = 40,
    min_duration: float = 1.2,
    audio_duration_ceiling: Optional[float] = None,
    highlight_keywords: Optional[list] = None,
) -> str:
    """
    Wraps subtitle cue text, enforces a minimum display duration threshold,
    resolves chronological cue overlaps, and optionally clamps trailing cues to the voiceover
    audio duration ceiling to guarantee smooth, collision-free playback.
    """
    if not srt_content:
        return ""

    blocks = srt_content.strip().split("\n\n")
    parsed_cues = []

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            timing = lines[1]
            cue_text = " ".join(lines[2:])

            if " --> " in timing:
                start_str, end_str = timing.split(" --> ")
                start_sec = parse_srt_timestamp(start_str.strip())
                end_sec = parse_srt_timestamp(end_str.strip())
                if end_sec - start_sec < min_duration:
                    end_sec = start_sec + min_duration
                parsed_cues.append((start_sec, end_sec, cue_text))
            else:
                parsed_cues.append((0.0, min_duration, cue_text))

    # Sort chronologically by start timestamp
    parsed_cues.sort(key=lambda x: x[0])

    # Deduplicate / adjust overlaps so cues don't collide
    # Clamp preceding cue's end if next cue starts earlier, ensuring a tiny 50ms buffer
    adjusted_cues = []
    for i in range(len(parsed_cues)):
        start_sec, end_sec, cue_text = parsed_cues[i]
        if i + 1 < len(parsed_cues):
            next_start = parsed_cues[i + 1][0]
            if end_sec > next_start:
                end_sec = max(start_sec + 0.1, next_start - 0.05)
        if end_sec <= start_sec:
            end_sec = start_sec + min_duration
        adjusted_cues.append((start_sec, end_sec, cue_text))

    formatted_blocks = []
    for idx, (start_sec, end_sec, cue_text) in enumerate(adjusted_cues, start=1):
        # Optionally clamp cue to audio duration ceiling
        if audio_duration_ceiling is not None and audio_duration_ceiling > 0:
            if start_sec >= audio_duration_ceiling:
                # Do not emit cues that start after the audio has completely terminated
                continue
            if end_sec > audio_duration_ceiling:
                end_sec = audio_duration_ceiling

        timing = (
            f"{format_srt_timestamp(start_sec)} --> {format_srt_timestamp(end_sec)}"
        )
        # Normalize whitespace and ensure clean word wrapping without breaking mid-word
        clean_text = " ".join(cue_text.strip().split())

        # If highlight keywords provided, format keywords for emphasis
        if highlight_keywords:
            import re

            for kw in highlight_keywords:
                pattern = re.compile(rf"\b({re.escape(kw)})\b", re.IGNORECASE)
                clean_text = pattern.sub(r"<\1>", clean_text)

        wrapped_lines = textwrap.wrap(
            clean_text, width=max_line_length, break_long_words=False
        )
        formatted_blocks.append(f"{idx}\n{timing}\n" + "\n".join(wrapped_lines))

    return "\n\n".join(formatted_blocks) + "\n"


async def _generate_audio_async(text, output_path, voice="en-US-ChristopherNeural"):
    """
    Asynchronously generates TTS audio from text using edge-tts.
    Also generates a corresponding .srt subtitle file.

    Args:
        text (str): The text to synthesize.
        output_path (str): The path to save the generated MP3 file.
        voice (str): The voice model to use.
    """
    communicate = edge_tts.Communicate(text, voice)

    sub_maker = edge_tts.SubMaker()
    word_boundary_seen = False
    buffered_sentence_chunks = []

    with open(output_path, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                word_boundary_seen = True
                sub_maker.feed(chunk)
            elif chunk["type"] == "SentenceBoundary":
                # Buffer sentence boundary in case word boundaries are absent from TTS stream
                buffered_sentence_chunks.append(chunk)

    # If no fine-grained WordBoundary chunks were emitted, feed SentenceBoundaries as fallback
    if not word_boundary_seen and buffered_sentence_chunks:
        logger.debug(
            "No WordBoundary chunks received; falling back to SentenceBoundary chunks."
        )
        for s_chunk in buffered_sentence_chunks:
            sub_maker.feed(s_chunk)

    srt_output_path = os.path.splitext(output_path)[0] + ".srt"
    srt_content = sub_maker.get_srt().strip()

    # Validate that subtitle content is non-empty; if empty, provide a valid fallback block
    if not srt_content:
        logger.warning(
            f"SubMaker generated empty subtitles for '{text[:30]}...'. Synthesizing fallback subtitle block."
        )
        # Approximate duration based on word count (150 words per minute ~ 2.5 words/sec)
        words = len(text.split())
        approx_secs = max(3, math.ceil(words / 2.5))
        m, s = divmod(approx_secs, 60)
        end_time_str = f"00:{m:02d}:{s:02d},000"
        srt_content = f"1\n00:00:00,000 --> {end_time_str}\n{text}\n"

    # Format cues to wrap cleanly on portrait aspect ratios
    formatted_srt = format_subtitle_cues(srt_content, max_line_length=40)

    with open(srt_output_path, "w", encoding="utf-8") as file:
        file.write(formatted_srt)


def generate_voiceover(text, output_path, voice="en-US-ChristopherNeural"):
    """
    Synchronous wrapper to generate TTS audio from text using edge-tts.
    Creates directories if they do not exist.

    Args:
        text (str): The text to synthesize.
        output_path (str): The path to save the generated MP3 file.
        voice (str): The voice model to use.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    asyncio.run(_generate_audio_async(text, output_path, voice))


def generate_all_voiceovers(config):
    """
    Generates all voiceover tracks required by the configuration scenes.

    Args:
        config (dict): The parsed job configuration.
    """
    for scene in config.get("scenes", []):
        text = scene.get("text")
        output_path = scene.get("voiceover_path")

        if not os.path.exists(output_path):
            logger.info(f"Generating voiceover for scene {scene.get('sequence')}...")
            generate_voiceover(text, output_path)
        else:
            logger.debug(
                f"Voiceover already exists for scene {scene.get('sequence')}: {output_path}"
            )
