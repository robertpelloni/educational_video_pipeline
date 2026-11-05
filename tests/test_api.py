import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch
from unittest.mock import MagicMock
from src.api_router import app

client = TestClient(app)

# Default valid credentials for tests
auth_headers = {
    "Authorization": "Basic YWRtaW46bG9jYWxfZGV2X3Bhc3N3b3Jk"
}  # admin:local_dev_password


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
def test_generate_video_endpoint_unauthorized():
    payload = {"topic": "Black hole"}
    response = client.post("/generate", json=payload)
    assert response.status_code == 401


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
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


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
def test_generate_video_endpoint_empty_topic():
    payload = {"topic": "   ", "skip_upload": True}

    with patch("src.api_router.run_pipeline_task.delay") as mock_delay:
        mock_delay.return_value.id = "test-task-id-123"
        response = client.post("/generate", json=payload, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["topic"] == "Random Educational Topic"


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
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


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
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


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
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


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
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


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
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


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
def test_generate_video_endpoint_wrong_type_boolean():
    from src.api_router import limiter

    limiter.reset()

    payload = {"topic": "Valid Topic", "skip_upload": "not_a_bool"}

    with patch("src.api_router.run_pipeline_task.delay") as mock_delay:
        mock_delay.return_value.id = "test-task-id-123"
        response = client.post("/generate", json=payload, headers=auth_headers)

    assert response.status_code == 200
    mock_delay.assert_called_once_with("Valid Topic", True)


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
def test_submit_video_endpoint_empty_topic():
    from src.api_router import limiter

    limiter.reset()
    payload = {"topic": "   ", "skip_upload": True}
    response = client.post("/submit", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert "Random Educational Topic" in response.json()["message"]


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
def test_submit_video_endpoint_missing_payload():
    from src.api_router import limiter

    limiter.reset()
    response = client.post("/submit", json={}, headers=auth_headers)
    assert response.status_code == 200
    assert "Random Educational Topic" in response.json()["message"]


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
def test_submit_video_endpoint_rate_limiting():
    from src.api_router import limiter

    limiter.reset()

    payload = {"topic": "Rate Limit Test", "skip_upload": True}
    for _ in range(5):
        response = client.post("/submit", json=payload, headers=auth_headers)
        assert response.status_code == 200

    response = client.post("/submit", json=payload, headers=auth_headers)
    assert response.status_code == 429


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
def test_status_endpoint():
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["api_version"] == "0.4.0"
    assert "redis_connected" in data


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
def test_auth_verify_endpoint():
    response = client.post("/auth/verify", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "authenticated"
    assert response.json()["user"] == "admin"


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
def test_tasks_endpoint_polling():
    with patch("src.api_router.celery_app.AsyncResult") as mock_async:
        mock_result = MagicMock()
        mock_result.status = "SUCCESS"
        mock_result.ready.return_value = True
        mock_result.result = {"videos": ["video_landscape.mp4"]}
        mock_async.return_value = mock_result

        response = client.get("/tasks/task-999", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "task-999"
        assert data["status"] == "SUCCESS"
        assert data["ready"] is True
        assert data["result"]["videos"] == ["video_landscape.mp4"]


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
def test_orders_lifecycle_endpoints():
    with patch("src.api_router.transition_order_status.delay") as mock_task:
        mock_task.return_value.id = "order-task-456"
        payload = {"order_id": "ORD-99", "new_status": "SHIPPED"}
        post_resp = client.post("/orders", json=payload, headers=auth_headers)
        assert post_resp.status_code == 200
        assert post_resp.json()["order_id"] == "ORD-99"
        assert post_resp.json()["task_id"] == "order-task-456"

    get_resp = client.get("/orders/ORD-99", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["order_id"] == "ORD-99"
    assert get_resp.json()["status"] == "CONFIRMED"


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
def test_validate_config_endpoint():
    valid_cfg = {
        "project_id": "test_proj",
        "canvas_format": "landscape",
        "background_music": "music.mp3",
        "global_music_volume_db": -18.0,
        "scenes": [
            {
                "sequence": 1,
                "text": "Intro text",
                "image_path": "scene.png",
                "voiceover_path": "scene.mp3",
            }
        ],
        "youtube_metadata": {
            "title": "Title",
            "description": "Desc",
            "tags": ["tag"],
            "category_id": "27",
        },
    }
    resp = client.post(
        "/validate-config", json={"config": valid_cfg}, headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is True

    invalid_cfg = {"project_id": "missing_scenes"}
    resp = client.post(
        "/validate-config", json={"config": invalid_cfg}, headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is False
    assert "error" in resp.json()


@patch.dict(os.environ, {"API_PASSWORD": "local_dev_password"})
def test_analytics_endpoint():
    with patch("src.api_router.fetch_platform_analytics") as mock_analytics:
        mock_analytics.return_value = {
            "metrics": {"youtube": {"views": 1200}},
            "feedback_summary": "High engagement",
        }
        resp = client.get("/analytics/proj_xyz", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["project_id"] == "proj_xyz"
        assert resp.json()["feedback_summary"] == "High engagement"
