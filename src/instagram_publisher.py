import os
import time
import logging
import requests

logger = logging.getLogger(__name__)


def get_instagram_credentials():
    """Retrieves Instagram Graph API credentials from the environment."""
    access_token = os.environ.get("IG_ACCESS_TOKEN")
    ig_user_id = os.environ.get("IG_USER_ID")

    if not access_token or not ig_user_id:
        logger.warning(
            "Missing Instagram Graph API credentials in environment. Falling back to stub."
        )
        return None
    return access_token, ig_user_id


def upload_video(video_url, metadata):
    """
    Uploads a video to Instagram Reels using the Facebook Graph API.
    Note: The Graph API requires a publicly accessible video URL, not a local file path.
    If credentials are not found, falls back to stub execution for local dev.
    """
    # For local files, we'd normally upload to an S3 bucket or similar first.
    # We will assume video_url is a local path and raise a warning for this implementation,
    # or that the system has already hoisted it.

    logger.info(f"Preparing to upload {video_url} to Instagram Reels...")

    credentials = get_instagram_credentials()
    if not credentials:
        logger.info("Upload to Instagram Reels Successful (Stub)! Video ID: stub_ig_id")
        return "stub_ig_id"

    access_token, ig_user_id = credentials

    caption = f"{metadata.get('title', 'Video')}\n\n{metadata.get('description', '')}"
    tags = metadata.get("tags", [])
    if tags:
        caption += "\n" + " ".join([f"#{tag.replace(' ', '')}" for tag in tags])

    graph_url = "https://graph.facebook.com/v19.0"

    try:
        # Step 1: Create the media container
        logger.info("Initializing Instagram Reels media container...")
        container_url = f"{graph_url}/{ig_user_id}/media"
        container_payload = {
            "media_type": "REELS",
            "video_url": video_url,  # Must be a public URL in production
            "caption": caption,
            "access_token": access_token,
        }

        response = None
        response = requests.post(container_url, data=container_payload)
        response.raise_for_status()
        container_id = response.json().get("id")

        if not container_id:
            raise RuntimeError(
                "Failed to retrieve container ID from Instagram Graph API."
            )

        logger.info(
            f"Container created successfully. ID: {container_id}. Waiting for processing..."
        )

        # Step 2: Poll container status (simplified)
        # Real implementations should poll the status endpoint until status_code == "FINISHED"
        time.sleep(5)

        # Step 3: Publish the container
        logger.info("Publishing the Instagram Reels container...")
        publish_url = f"{graph_url}/{ig_user_id}/media_publish"
        publish_payload = {"creation_id": container_id, "access_token": access_token}

        publish_response = requests.post(publish_url, data=publish_payload)
        publish_response.raise_for_status()

        media_id = publish_response.json().get("id")
        logger.info(f"Upload to Instagram Reels Successful! Media ID: {media_id}")
        return str(media_id)

    except requests.RequestException as e:
        logger.error(f"Instagram Graph API upload failed: {e}")
        if response and hasattr(response, "text"):
            logger.error(f"API Response: {response.text}")
        raise RuntimeError(f"Failed to publish to Instagram: {e}")
