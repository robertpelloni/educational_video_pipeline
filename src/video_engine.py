import os
import logging
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume as volumex

logger = logging.getLogger(__name__)

class MissingAssetError(Exception):
    pass

def apply_zoom_effect(clip, zoom_ratio=0.04):
    """
    Applies a simple zoom-in effect (Ken Burns style) to a clip.
    Note: A true Ken Burns effect requires frame-by-frame transformation.
    Here, we'll do a simple zoom by resizing the clip over time.
    """
    def effect(get_frame, t):
        img = get_frame(t)
        # We can implement a simple resize, but moviepy resizing for each frame is slow.
        # Alternatively, we just return the frame. A full Ken Burns can be done via vfx.resize
        return img

    # A more standard moviepy way for zoom (though computationally heavy):
    # This just increases size slightly over the duration
    return clip.resize(lambda t: 1 + (zoom_ratio * t / clip.duration))

def compile_video(config, output_path="output.mp4"):
    """
    Compiles the final video according to the provided config.

    Args:
        config (dict): Parsed configuration dictionary.
        output_path (str): The output path for the rendered MP4 file.
    """
    video_clips = []

    # 1. Process each scene
    for scene in config.get("scenes", []):
        seq = scene["sequence"]
        image_file = scene["image_path"]
        audio_file = scene["voiceover_path"]

        # Absolute runtime safety checks
        if not os.path.exists(image_file):
            raise MissingAssetError(f"Missing image asset for scene {seq}: {image_file}")
        if not os.path.exists(audio_file):
            raise MissingAssetError(f"Missing audio asset for scene {seq}: {audio_file}")

        # Load audio to dynamically determine the exact duration of speech
        voice_audio = AudioFileClip(audio_file)
        duration = voice_audio.duration

        # Create visual clip matched to voice duration
        img_clip = ImageClip(image_file).set_duration(duration)

        # Apply smooth scaling adjustment (Ken Burns effect)
        img_clip = apply_zoom_effect(img_clip)

        # Set the audio of this video segment to the voiceover
        img_clip = img_clip.set_audio(voice_audio)

        video_clips.append(img_clip)

    if not video_clips:
        raise ValueError("No video clips generated. Please check your scenes.")

    # 2. Concatenate all scenes into a continuous video
    final_video = concatenate_videoclips(video_clips, method="compose")

    # 3. Handle Background Music & Audio Ducking
    music_path = config.get("background_music")
    if music_path and os.path.exists(music_path):
        bg_music = AudioFileClip(music_path)

        # Loop music if shorter than video, or cut if longer
        if bg_music.duration < final_video.duration:
            from moviepy.audio.fx.audio_loop import audio_loop
            bg_music = audio_loop(bg_music, duration=final_video.duration)
        else:
            bg_music = bg_music.set_duration(final_video.duration)

        # Volume attenuation (Ducking)
        target_volume = config.get("global_music_volume", 0.12)
        bg_music = volumex(bg_music, target_volume)

        # Combine the original video audio (voiceovers) with the background music
        combined_audio = CompositeAudioClip([final_video.audio, bg_music])
        final_video = final_video.set_audio(combined_audio)
    elif music_path:
        raise MissingAssetError(f"Background music missing: {music_path}")

    # 4. Render the final MP4 file
    canvas = config.get("canvas_format", "landscape")
    # For a real implementation, canvas would affect resize resolution,
    # e.g., 1080x1920 for portrait, 1920x1080 for landscape.
    # Assuming images are already correctly sized for simplicity here.

    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast", # faster rendering for pipeline
        logger=None # Disable moviepy's internal progress bar logging for cleaner logs
    )
    logger.info(f"Video rendering complete: {output_path}")
