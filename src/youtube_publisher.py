import os
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def authenticate_youtube():
    """Authenticates the user using client_secrets.json and returns a youtube service object."""
    credentials = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        credentials = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists('client_secrets.json'):
                raise FileNotFoundError("Missing client_secrets.json for YouTube authentication.")
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            credentials = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token_file:
            token_file.write(credentials.to_json())

    return build('youtube', 'v3', credentials=credentials)

def upload_video(video_path, metadata):
    """
    Uploads a video to YouTube securely via the YouTube Data API v3.

    Args:
        video_path (str): The path to the video file to upload.
        metadata (dict): Metadata dictionary containing title, description, tags, and category_id.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    youtube = authenticate_youtube()

    body = {
        'snippet': {
            'title': metadata.get('title', 'Automated Video'),
            'description': metadata.get('description', ''),
            'tags': metadata.get('tags', []),
            'categoryId': metadata.get('category_id', '27') # 27 = Education
        },
        'status': {
            'privacyStatus': 'private' # Hardcoded to private by default for review
        }
    }

    logger.info(f"Preparing to upload {video_path}...")

    # Ensure resumable=True for chunked transfers
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype='video/*')

    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logger.info(f"Upload Progress: {int(status.progress() * 100)}%")

    logger.info(f"Upload Successful! Video ID: {response['id']}")
    return response['id']
