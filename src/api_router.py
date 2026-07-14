import os

import logging
import secrets
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from pydantic import BaseModel, Field

from src.worker import run_pipeline_task

logger = logging.getLogger(__name__)

security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Authentication to protect the generation endpoint using environment variables."""
    expected_username = os.environ.get("API_USERNAME", "admin")
    expected_password = os.environ.get("API_PASSWORD")

    if not expected_password:
        logger.error(
            "API_PASSWORD environment variable is not set. API is locked down."
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error. Authentication unavailable.",
        )

    correct_username = secrets.compare_digest(credentials.username, expected_username)
    correct_password = secrets.compare_digest(credentials.password, expected_password)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Educational Video Pipeline API",
    description="REST endpoint to trigger autonomous video generation",
    version="0.1.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


class GenerateRequest(BaseModel):
    topic: str = Field(..., max_length=255)
    skip_upload: bool = Field(default=True)


@app.post(
    "/generate",
    responses={
        400: {"description": "Bad Request - Empty topic"},
        401: {"description": "Unauthorized"},
        429: {"description": "Too Many Requests"}
    }
)
@limiter.limit("5/minute")
async def generate_video(
    request: Request,
    payload: GenerateRequest,
    username: str = Depends(verify_credentials),
):
    topic_clean = payload.topic.strip()
    if not topic_clean:
        raise HTTPException(
            status_code=400, detail="The provided topic cannot be empty."
        )

    # Dispatch the job to the distributed Celery queue
    task = run_pipeline_task.delay(topic_clean, payload.skip_upload)

    return {
        "status": "success",
        "message": f"Pipeline generation dispatched to queue for topic: '{topic_clean}'",
        "task_id": task.id,
        "topic": topic_clean,
    }
