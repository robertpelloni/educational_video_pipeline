import os
import logging
import tweepy

logger = logging.getLogger(__name__)

def get_twitter_client():
    """Initializes Tweepy Client using environment variables."""
    api_key = os.environ.get("TWITTER_API_KEY")
    api_secret = os.environ.get("TWITTER_API_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

    if not all([api_key, api_secret, access_token, access_token_secret]):
        logger.warning("Missing Twitter API credentials in environment. Falling back to stub.")
        return None

    # Tweepy Client for v2 API endpoints
    client = tweepy.Client(
        consumer_key=api_key, consumer_secret=api_secret,
        access_token=access_token, access_token_secret=access_token_secret
    )

    # Tweepy API for v1.1 endpoints (Media Uploads currently rely on v1.1)
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
    api = tweepy.API(auth)

    return client, api


def upload_video(video_path, metadata):
    """
    Uploads a video to X (Twitter) using the chunked media upload endpoint.
    If credentials are not found, falls back to stub execution for local dev.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    logger.info(f"Preparing to upload {video_path} to X (Twitter)...")

    twitter_clients = get_twitter_client()
    if not twitter_clients:
        logger.info(f"Upload to X (Twitter) Successful (Stub)! Video ID: stub_x_id")
        return "stub_x_id"

    client, api = twitter_clients

    try:
        # Step 1: Upload media via v1.1 chunked endpoint
        logger.info("Initiating chunked media upload to Twitter...")
        media = api.media_upload(filename=video_path, media_category="tweet_video")

        # We need to wait for processing to finish if the video is large
        # But tweepy handles the basic INIT/APPEND/FINALIZE in `media_upload` by default for simple files.
        # Note: robust asynchronous polling of media processing status would go here.

        # Step 2: Create Tweet via v2 API
        tweet_text = f"{metadata.get('title', 'Video')}\n\n{metadata.get('description', '')}"

        # Append tags
        tags = metadata.get("tags", [])
        if tags:
            tweet_text += "\n" + " ".join([f"#{tag.replace(' ', '')}" for tag in tags])

        logger.info("Publishing tweet with attached media...")
        response = client.create_tweet(text=tweet_text, media_ids=[media.media_id])

        tweet_id = response.data['id']
        logger.info(f"Upload to X (Twitter) Successful! Tweet ID: {tweet_id}")
        return str(tweet_id)

    except tweepy.TweepyException as e:
        logger.error(f"Twitter API upload failed: {e}")
        raise RuntimeError(f"Failed to publish to Twitter: {e}")
