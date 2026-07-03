import argparse
import logging
import sys

from src.config import load_config
from src.audio_engine import generate_all_voiceovers
from src.video_engine import compile_video
from src.youtube_publisher import upload_video

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="Automated Video Generation and YouTube Publishing Pipeline.")
    parser.add_argument("--config", type=str, required=True, help="Path to the JSON job configuration file.")
    parser.add_argument("--output", type=str, default="final_video.mp4", help="Path to save the generated video.")
    parser.add_argument("--skip-upload", action="store_true", help="Skip the YouTube upload step.")

    args = parser.parse_args()

    try:
        # Step 1: Parse and validate configuration
        logger.info(f"Loading configuration from {args.config}...")
        config = load_config(args.config)

        # Step 2: Generate TTS audio clips
        logger.info("Checking and generating voiceovers...")
        generate_all_voiceovers(config)

        # Step 3: Compile video
        logger.info("Compiling video...")
        compile_video(config, output_path=args.output)

        # Step 4: Upload to YouTube (if not skipped)
        if not args.skip_upload:
            logger.info("Initiating YouTube upload...")
            upload_video(args.output, config.get("youtube_metadata", {}))
        else:
            logger.info("Skipping YouTube upload as requested.")

        logger.info("Pipeline execution completed successfully.")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
