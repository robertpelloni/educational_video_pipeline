import asyncio
import math
import os
import logging
import edge_tts

logger = logging.getLogger(__name__)


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

    with open(srt_output_path, "w", encoding="utf-8") as file:
        file.write(srt_content)


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
