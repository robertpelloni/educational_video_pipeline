import os
import math
import logging
import ffmpeg

logger = logging.getLogger(__name__)


class MissingAssetError(Exception):
    pass


def get_audio_duration(file_path: str) -> float:
    """Helper to extract audio duration using ffprobe."""
    try:
        probe = ffmpeg.probe(file_path)
        return float(probe["format"]["duration"])
    except ffmpeg.Error as e:
        logger.error(f"ffprobe error: {e.stderr.decode('utf-8')}")
        raise ValueError(f"Failed to probe audio duration for {file_path}")


def compile_video(config: dict, output_path: str = "output.mp4"):
    """
    Compiles the final video according to the provided config using hardware-accelerated ffmpeg.

    Args:
        config (dict): Parsed configuration dictionary.
        output_path (str): The output path for the rendered MP4 file.
    """
    canvas_format = config.get("canvas_format", "landscape")
    target_w, target_h = (1080, 1920) if canvas_format == "portrait" else (1920, 1080)

    video_streams = []
    audio_streams = []

    # 1. Process each scene
    for scene in config.get("scenes", []):
        seq = scene["sequence"]
        image_file = scene["image_path"]
        audio_file = scene["voiceover_path"]

        # Absolute runtime safety checks
        if not os.path.exists(image_file):
            raise MissingAssetError(
                f"Missing image asset for scene {seq}: {image_file}"
            )
        if not os.path.exists(audio_file):
            raise MissingAssetError(
                f"Missing audio asset for scene {seq}: {audio_file}"
            )

        # Get exact duration of speech
        duration = get_audio_duration(audio_file)

        # Video: Input image, loop for duration, scale/crop, apply basic "zoom" pan effect
        # zoompan generates frames internally, so we don't loop the input image
        v_stream = (
            ffmpeg.input(image_file)
            .filter(
                "scale",
                w=f"max(iw,ih*({target_w}/{target_h}))",
                h=f"max(ih,iw*({target_h}/{target_w}))",
            )
            .filter("crop", w=target_w, h=target_h)
            .filter(
                "zoompan",
                z="min(zoom+0.001,1.04)",
                d=math.ceil(duration * 24),
                s=f"{target_w}x{target_h}",
                fps=24,
            )
            .filter("setsar", "1")  # Ensure square pixels
        )

        # Audio: Input voiceover
        a_stream = ffmpeg.input(audio_file)

        video_streams.append(v_stream)
        audio_streams.append(a_stream)

    if not video_streams:
        raise ValueError("No video clips generated. Please check your scenes.")

    # 2. Concatenate all scenes sequentially
    joined_video = ffmpeg.concat(*video_streams, v=1, a=0)
    joined_audio = ffmpeg.concat(*audio_streams, v=0, a=1)

    # 3. Handle Background Music & Audio Ducking
    music_path = config.get("background_music")
    if music_path and os.path.exists(music_path):
        target_db = config.get("global_music_volume_db", -18.0)

        # Input background music, loop infinitely if short, and apply volume
        bg_audio = ffmpeg.input(music_path, stream_loop=-1).filter(
            "volume", f"{target_db}dB"
        )

        # Mix the voiceovers and background music together
        # amix automatically drops to the shortest input if we use duration='first'
        final_audio = ffmpeg.filter(
            [joined_audio, bg_audio], "amix", inputs=2, duration="first"
        )
    else:
        if music_path:
            logger.warning(f"Background music missing: {music_path}. Continuing without ducking.")
        final_audio = joined_audio

    # 4. Render the final MP4 file
    logger.info(f"Executing FFmpeg render to {output_path}...")

    try:
        out = ffmpeg.output(
            joined_video,
            final_audio,
            output_path,
            vcodec="libx264",
            acodec="aac",
            preset="ultrafast",
            r=24,  # framerate
            pix_fmt="yuv420p",
            shortest=None,  # end when shortest stream ends (the video/voiceover track)
        )
        # overwrite output
        out = ffmpeg.overwrite_output(out)
        out.run(quiet=True)  # quiet=True hides ffmpeg spam, raising errors cleanly
        logger.info(f"Video rendering complete: {output_path}")
    except ffmpeg.Error as e:
        logger.error(f"FFmpeg render failed: {e.stderr.decode('utf-8')}")
        raise ValueError("FFmpeg rendering pipeline crashed.")
