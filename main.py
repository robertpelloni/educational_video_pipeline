import argparse
import logging
import sys

import os
import jsonschema

from src.config import load_config, SCHEMA
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


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(
        description="Automated Video Generation and YouTube Publishing Pipeline."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--config", type=str, help="Path to a JSON job configuration file."
    )
    group.add_argument(
        "--topic",
        type=str,
        help="A topic to generate a video about automatically via Wikipedia.",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="final_video.mp4",
        help="Path to save the generated video.",
    )
    parser.add_argument(
        "--skip-upload", action="store_true", help="Skip the YouTube upload step."
    )

    args = parser.parse_args()

    try:
        if args.topic is not None:
            topic_clean = args.topic.strip()
            if not topic_clean:
                raise ValueError(
                    "The provided --topic argument cannot be empty or just whitespace."
                )

            logger.info(
                f"Initiating autonomous end-to-end generation for topic: '{topic_clean}'"
            )

            project_id = topic_clean.lower().replace(" ", "_")

            # 1a. Analytics Polling
            analytics_data = fetch_platform_analytics(project_id)
            feedback_summary = analytics_data.get("feedback_summary")

            # 1b. Ingestion
            raw_text = fetch_wikipedia_summary(topic_clean)

            # 1c. LLM Structure
            config = generate_script_from_text(raw_text, project_id=project_id, analytics_feedback=feedback_summary)
            jsonschema.validate(instance=config, schema=SCHEMA)

            # 1d. Image Generation
            logger.info("Generating visual assets...")
            for scene in config.get("scenes", []):
                image_path = scene.get("image_path")
                if image_path and not os.path.exists(image_path):
                    # We use a simple prompt derived from the scene text for the image generator
                    prompt = f"Educational illustration regarding: {scene.get('text')}"
                    generate_image_from_prompt(prompt, image_path)

        else:
            # Step 1: Parse and validate explicit file configuration
            logger.info(f"Loading configuration from {args.config}...")
            config = load_config(args.config)

        # Step 2: Generate TTS audio clips
        logger.info("Checking and generating voiceovers...")
        generate_all_voiceovers(config)

        # Step 3: Compile video
        logger.info("Compiling video...")
        canvas_formats = config.get("canvas_format", ["landscape"])
        if isinstance(canvas_formats, str):
            canvas_formats = [canvas_formats]

        output_paths = []
        for fmt in canvas_formats:
            fmt_output_path = args.output.replace(".mp4", f"_{fmt}.mp4")
            compile_video(config, output_path=fmt_output_path, canvas_format=fmt)
            output_paths.append(fmt_output_path)

        # Step 4: Upload to platforms (if not skipped)
        if not args.skip_upload:
            platforms = config.get("platforms", ["youtube"])
            metadata = config.get("youtube_metadata", {})
            for platform in platforms:
                # Naive routing: pass the first rendered output, in real life you'd route specific formats to specific platforms
                upload_target = output_paths[0]
                if platform in ["tiktok", "instagram"] and "portrait" in canvas_formats:
                    upload_target = next((p for p in output_paths if "portrait" in p), upload_target)
                elif platform == "youtube" and "landscape" in canvas_formats:
                    upload_target = next((p for p in output_paths if "landscape" in p), upload_target)

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

        logger.info("Pipeline execution completed successfully.")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
