import asyncio
import os
import logging
import edge_tts

logger = logging.getLogger(__name__)

async def _generate_audio_async(text, output_path, voice="en-US-ChristopherNeural"):
    """
    Asynchronously generates TTS audio from text using edge-tts.

    Args:
        text (str): The text to synthesize.
        output_path (str): The path to save the generated MP3 file.
        voice (str): The voice model to use.
    """
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

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
            logger.debug(f"Voiceover already exists for scene {scene.get('sequence')}: {output_path}")
