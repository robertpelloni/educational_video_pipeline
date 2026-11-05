import os
import logging
import secrets
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, Field, field_validator
from typing import Any, List, Optional
import jsonschema

from src.worker import run_pipeline_task, transition_order_status, celery_app
from src.analytics_engine import fetch_platform_analytics
from src.config import SCHEMA

logger = logging.getLogger(__name__)

security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Authentication to protect sensitive endpoints using environment variables."""
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
    description="REST endpoint to trigger and manage autonomous video generation",
    version="0.4.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


class GenerateRequest(BaseModel):
    topic: str = Field(default="Random Educational Topic")
    skip_upload: bool = Field(default=True)
    canvas_format: Optional[List[str]] = Field(default=None)
    platforms: Optional[List[str]] = Field(default=None)

    @field_validator("topic", mode="before")
    def validate_topic(cls, v: Any) -> str:
        if not v or not isinstance(v, str) or not v.strip():
            return "Random Educational Topic"
        return v[:255]

    @field_validator("skip_upload", mode="before")
    def validate_skip_upload(cls, v: Any) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str) and v.lower() in ["false", "0", "no"]:
            return False
        return True


class OrderRequest(BaseModel):
    order_id: str = Field(default="ORD-001")
    new_status: str = Field(default="PROCESSING")


class ValidateConfigRequest(BaseModel):
    config: dict


@app.get("/status")
def get_service_status():
    """Returns the operational status of the API, Redis broker, and Celery worker."""
    redis_alive = False
    try:
        import redis

        redis_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
        r = redis.from_url(redis_url, socket_timeout=1)
        redis_alive = bool(r.ping())
    except Exception:
        redis_alive = False

    return {
        "status": "online",
        "api_version": "0.4.0",
        "redis_connected": redis_alive,
        "celery_broker": os.environ.get(
            "CELERY_BROKER_URL", "redis://localhost:6379/0"
        ),
    }


@app.post(
    "/auth/verify",
    responses={
        401: {"description": "Unauthorized"},
        500: {"description": "Internal Server Error"},
    },
)
def verify_auth_token(username: str = Depends(verify_credentials)):
    """Verifies credentials for dynamic frontend auth refresh handshakes."""
    return {"status": "authenticated", "user": username}


@app.post(
    "/generate",
    responses={
        400: {"description": "Bad Request - Empty topic"},
        401: {"description": "Unauthorized"},
        429: {"description": "Too Many Requests"},
    },
)
@limiter.limit("5/minute")
async def generate_video(
    request: Request,
    payload: GenerateRequest,
    username: str = Depends(verify_credentials),
):
    topic_clean = payload.topic.strip()

    # Dispatch the job to the distributed Celery queue
    task = run_pipeline_task.delay(topic_clean, payload.skip_upload)

    return {
        "status": "success",
        "message": f"Pipeline generation dispatched to queue for topic: '{topic_clean}'",
        "task_id": task.id,
        "topic": topic_clean,
    }


@app.post(
    "/submit",
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        429: {"description": "Too Many Requests"},
    },
)
@limiter.limit("5/minute")
async def submit_video(
    request: Request,
    payload: GenerateRequest,
    username: str = Depends(verify_credentials),
):
    topic_clean = payload.topic.strip()
    return {"status": "success", "message": f"Submission received for: '{topic_clean}'"}


@app.get("/tasks/{task_id}")
def get_task_status(task_id: str, username: str = Depends(verify_credentials)):
    """Polls Celery for the execution status of an asynchronous video generation task."""
    try:
        async_res = celery_app.AsyncResult(task_id)
        res_payload = {
            "task_id": task_id,
            "status": async_res.status,
            "ready": async_res.ready(),
        }
        if async_res.ready():
            res_payload["result"] = async_res.result
        return res_payload
    except Exception as e:
        logger.warning(f"Error querying task {task_id}: {e}")
        return {
            "task_id": task_id,
            "status": "UNKNOWN",
            "ready": False,
            "error": str(e),
        }


@app.post("/orders")
def create_order_transition(
    payload: OrderRequest, username: str = Depends(verify_credentials)
):
    """Dispatches a mock order state transition event to Celery worker."""
    task = transition_order_status.delay(payload.order_id, payload.new_status)
    return {
        "status": "dispatched",
        "order_id": payload.order_id,
        "new_status": payload.new_status,
        "task_id": task.id,
    }


@app.get("/orders/{order_id}")
def get_order_status(order_id: str, username: str = Depends(verify_credentials)):
    """Simulates querying mock order state."""
    return {
        "order_id": order_id,
        "status": "CONFIRMED",
        "fulfillment": "SIMULATED_ERP_READY",
    }


@app.post("/validate-config")
def validate_job_configuration(
    payload: ValidateConfigRequest, username: str = Depends(verify_credentials)
):
    """Validates arbitrary job configuration against the formal JSON schema."""
    try:
        jsonschema.validate(instance=payload.config, schema=SCHEMA)
        return {
            "valid": True,
            "message": "Configuration strictly matches project schema.",
        }
    except jsonschema.ValidationError as err:
        return {"valid": False, "error": err.message}


@app.get("/analytics/{project_id}")
def get_analytics(project_id: str, username: str = Depends(verify_credentials)):
    """Exposes real-time cross-platform feedback metrics for a specific project."""
    data = fetch_platform_analytics(project_id)
    return {
        "project_id": project_id,
        "metrics": data.get("metrics"),
        "feedback_summary": data.get("feedback_summary"),
    }
