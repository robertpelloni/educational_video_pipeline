import os
import logging
import requests

logger = logging.getLogger(__name__)


def get_tiktok_credentials():
    """Retrieves TikTok API credentials from the environment."""
    access_token = os.environ.get("TIKTOK_ACCESS_TOKEN")
    open_id = os.environ.get("TIKTOK_OPEN_ID")

    if not access_token or not open_id:
        logger.warning(
            "Missing TikTok API credentials in environment. Falling back to stub."
        )
        return None
    return access_token, open_id


def upload_video(video_path, metadata):
    """
    Uploads a video to TikTok using the Content Posting API.
    If credentials are not found, falls back to stub execution for local dev.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    logger.info(f"Preparing to upload {video_path} to TikTok...")

    credentials = get_tiktok_credentials()
    if not credentials:
        logger.info("Upload to TikTok Successful (Stub)! Video ID: stub_tiktok_id")
        return "stub_tiktok_id"

    access_token, open_id = credentials

    # TikTok Content Posting API initialization endpoint
    init_url = "https://open-api.tiktok.com/share/video/upload/"

    try:
        # Step 1: Initialize the upload to get a publish_id
        logger.info("Initiating media upload to TikTok...")

        # This is a simplified direct upload POST for files under 50MB.
        # Larger files require a chunked upload sequence.
        with open(video_path, "rb") as f:
            files = {"video": f}
            data = {"open_id": open_id, "access_token": access_token}

            response = requests.post(init_url, files=files, data=data)
            response.raise_for_status()

            result = response.json()

            if result.get("error_code") != 0:
                raise RuntimeError(f"TikTok API Error: {result.get('error_msg')}")

            share_id = result.get("data", {}).get("share_id")

            if not share_id:
                raise RuntimeError("Failed to retrieve share_id from TikTok API.")

        logger.info(f"Upload to TikTok Successful! Share ID: {share_id}")
        return str(share_id)

    except requests.RequestException as e:
        logger.error(f"TikTok API upload failed: {e}")
        raise RuntimeError(f"Failed to publish to TikTok: {e}")
