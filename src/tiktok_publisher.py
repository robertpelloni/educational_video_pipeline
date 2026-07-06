import os
import logging

logger = logging.getLogger(__name__)


def upload_video(video_path, metadata):
    """
    Stubs an upload to TikTok.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    logger.info(f"Preparing to upload {video_path} to TikTok...")

    # Placeholder for actual TikTok API integration
    # TikTok API requires OAuth and a specific multipart upload flow
    # This is a stub for the architecture

    logger.info("Upload to TikTok Successful (Stub)! Video ID: stub_tiktok_id")
    return "stub_tiktok_id"
