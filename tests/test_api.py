import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api_router import app

client = TestClient(app)

# Default valid credentials for tests
auth_headers = {
    "Authorization": "Basic YWRtaW46c3VwZXJzZWNyZXRwaXBlbGluZQ=="
}  # admin:supersecretpipeline


@patch.dict(os.environ, {"API_PASSWORD": "supersecretpipeline"})
def test_generate_video_endpoint_unauthorized():
    payload = {"topic": "Black hole"}
    response = client.post("/generate", json=payload)
    assert response.status_code == 401


@patch.dict(os.environ, {"API_PASSWORD": "supersecretpipeline"})
def test_generate_video_endpoint_success():
    payload = {"topic": "Black hole", "skip_upload": True}

    with patch("src.api_router.run_pipeline_task.delay") as mock_delay:
        mock_delay.return_value.id = "test-task-id-123"
        response = client.post("/generate", json=payload, headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["topic"] == "Black hole"
        assert response.json()["task_id"] == "test-task-id-123"
        mock_delay.assert_called_once_with("Black hole", True)


@patch.dict(os.environ, {"API_PASSWORD": "supersecretpipeline"})
def test_generate_video_endpoint_empty_topic():
    payload = {"topic": "   ", "skip_upload": True}

    with patch("src.api_router.run_pipeline_task.delay") as mock_delay:
        mock_delay.return_value.id = "test-task-id-123"
        response = client.post("/generate", json=payload, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["topic"] == "Random Educational Topic"


@patch.dict(os.environ, {"API_PASSWORD": "supersecretpipeline"})
def test_generate_video_endpoint_missing_payload():
    with patch("src.api_router.run_pipeline_task.delay") as mock_delay:
        mock_delay.return_value.id = "test-task-id-123"
        response = client.post("/generate", json={}, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["topic"] == "Random Educational Topic"


@patch.dict(os.environ, clear=True)
def test_generate_video_endpoint_missing_server_config():
    """
    Tests edge case where the server itself is misconfigured and missing the API_PASSWORD.
    The system should securely lock down and return a 500 error.
    """
    payload = {"topic": "Black hole"}
    response = client.post("/generate", json=payload, headers=auth_headers)
    assert response.status_code == 500
    assert "Server configuration error" in response.json()["detail"]


@patch.dict(os.environ, {"API_PASSWORD": "supersecretpipeline"})
def test_generate_video_endpoint_invalid_credentials():
    """
    Tests edge case where basic auth headers are provided but the credentials are bad.
    """
    payload = {"topic": "Black hole"}
    bad_headers = {
        "Authorization": "Basic YWRtaW46YmFkcGFzc3dvcmQ="  # admin:badpassword
    }
    response = client.post("/generate", json=payload, headers=bad_headers)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


@patch.dict(os.environ, {"API_PASSWORD": "supersecretpipeline"})
def test_generate_video_endpoint_celery_broker_failure():
    """
    Tests edge case where the message broker (Redis) is down or Celery fails to queue the task.
    """
    payload = {"topic": "Black hole", "skip_upload": True}

    with patch("src.api_router.run_pipeline_task.delay") as mock_delay:
        # Simulate a connection error to Redis/Celery
        mock_delay.side_effect = ConnectionError("Connection to Redis failed")

        # FastAPI's default exception handler will catch unhandled exceptions and return a 500,
        # but we need to ensure our application raises an HTTP exception properly if we wanted to trap it.
        # Currently, api_router doesn't trap Celery errors, so it will bubble up as a 500 Internal Server Error.

        # We expect the test client to catch the 500.
        with pytest.raises(Exception):
            client.post("/generate", json=payload, headers=auth_headers)


@patch.dict(os.environ, {"API_PASSWORD": "supersecretpipeline"})
def test_generate_video_endpoint_rate_limiting():
    from src.api_router import limiter

    limiter.reset()
    """
    Tests edge case where rate limiting is triggered (HTTP 429).
    We dispatch 6 requests to hit the 5/minute limit.
    """
    payload = {"topic": "Rate Limit Test", "skip_upload": True}

    with patch("src.api_router.run_pipeline_task.delay") as mock_delay:
        mock_delay.return_value.id = "test-task-id-123"

        # Fire 5 successful requests
        for _ in range(5):
            response = client.post("/generate", json=payload, headers=auth_headers)
            assert response.status_code == 200

        # The 6th request should be rate limited
        response = client.post("/generate", json=payload, headers=auth_headers)
        assert response.status_code == 429

@patch.dict(os.environ, {"API_PASSWORD": "supersecretpipeline"})
def test_generate_video_endpoint_topic_too_long():
    from src.api_router import limiter
    limiter.reset()

    long_topic = "A" * 256
    payload = {"topic": long_topic, "skip_upload": True}

    with patch("src.api_router.run_pipeline_task.delay") as mock_delay:
        mock_delay.return_value.id = "test-task-id-123"
        response = client.post("/generate", json=payload, headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()["topic"]) == 255
    assert response.json()["topic"] == "A" * 255

@patch.dict(os.environ, {"API_PASSWORD": "supersecretpipeline"})
def test_generate_video_endpoint_wrong_type_boolean():
    from src.api_router import limiter
    limiter.reset()

    payload = {"topic": "Valid Topic", "skip_upload": "not_a_bool"}

    with patch("src.api_router.run_pipeline_task.delay") as mock_delay:
        mock_delay.return_value.id = "test-task-id-123"
        response = client.post("/generate", json=payload, headers=auth_headers)

    assert response.status_code == 200
    mock_delay.assert_called_once_with("Valid Topic", True)
