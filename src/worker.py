import os
import jsonschema
import logging
import re
from celery import Celery

from src.config import SCHEMA
from src.audio_engine import generate_all_voiceovers
from src.ffmpeg_engine import compile_video
from src.youtube_publisher import upload_video as youtube_upload
from src.tiktok_publisher import upload_video as tiktok_upload
from src.instagram_publisher import upload_video as instagram_upload
from src.twitter_publisher import upload_video as twitter_upload
from src.ingestion_engine import fetch_wikipedia_summary
from src.llm_engine import generate_script_from_text
from src.analytics_engine import fetch_platform_analytics
from src.image_engine import generate_image_from_prompt

logger = logging.getLogger(__name__)

# Configure Celery to use Redis (defaults to localhost:6379, typical for Docker setups)
redis_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery("video_pipeline", broker=redis_url, backend=redis_url)


@celery_app.task(name="run_video_pipeline_task")
def run_pipeline_task(topic: str, skip_upload: bool):
    """
    Executes the end-to-end video pipeline as a distributed Celery task.
    """
    logger.info(
        f"Celery Task: Initiating autonomous end-to-end generation for topic: '{topic}'"
    )
    try:
        project_id = re.sub(r"[^a-zA-Z0-9]", "_", topic.lower())

        # 1a. Analytics Polling
        analytics_data = fetch_platform_analytics(project_id)
        feedback_summary = analytics_data.get("feedback_summary")

        # 1b. Ingestion
        raw_text = fetch_wikipedia_summary(topic)

        # 1c. LLM Structure with Feedback Loop
        config = generate_script_from_text(
            raw_text, project_id=project_id, analytics_feedback=feedback_summary
        )
        jsonschema.validate(instance=config, schema=SCHEMA)

        # 1c. Image Generation
        logger.info("Generating visual assets...")
        for scene in config.get("scenes", []):
            image_path = scene.get("image_path")
            if image_path and not os.path.exists(image_path):
                prompt = f"Educational illustration regarding: {scene.get('text')}"
                generate_image_from_prompt(prompt, image_path)

        # 2: Generate TTS audio clips
        logger.info("Checking and generating voiceovers...")
        generate_all_voiceovers(config)

        # 3: Compile video
        base_output_path = f"assets/exports/{project_id}.mp4"
        os.makedirs(os.path.dirname(base_output_path), exist_ok=True)

        canvas_formats = config.get("canvas_format", ["landscape"])
        if isinstance(canvas_formats, str):
            canvas_formats = [canvas_formats]

        output_paths = []
        for fmt in canvas_formats:
            fmt_output_path = base_output_path.replace(".mp4", f"_{fmt}.mp4")
            logger.info(f"Compiling video to {fmt_output_path}...")
            compile_video(config, output_path=fmt_output_path, canvas_format=fmt)
            output_paths.append(fmt_output_path)

        # 4: Upload to platforms (if not skipped)
        if not skip_upload:
            platforms = config.get("platforms", ["youtube"])
            metadata = config.get("youtube_metadata", {})
            for platform in platforms:
                upload_target = output_paths[0]
                if platform in ["tiktok", "instagram"] and "portrait" in canvas_formats:
                    upload_target = next(
                        (p for p in output_paths if "portrait" in p), upload_target
                    )
                elif platform == "youtube" and "landscape" in canvas_formats:
                    upload_target = next(
                        (p for p in output_paths if "landscape" in p), upload_target
                    )

                logger.info(f"Initiating {platform} upload using {upload_target}...")
                if platform == "youtube":
                    youtube_upload(upload_target, metadata)
                elif platform == "tiktok":
                    tiktok_upload(upload_target, metadata)
                elif platform == "instagram":
                    instagram_upload(upload_target, metadata)
                elif platform == "twitter":
                    twitter_upload(upload_target, metadata)
        else:
            logger.info("Skipping uploads as requested.")

        logger.info(
            f"Pipeline Celery execution completed successfully for topic '{topic}'."
        )
        return {"status": "success", "topic": topic, "videos": output_paths}
    except Exception as e:
        logger.error(f"Pipeline Celery task failed: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
