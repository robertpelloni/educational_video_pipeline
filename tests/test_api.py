from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api_router import app

client = TestClient(app)

# Default valid credentials for tests
auth_headers = {
    "Authorization": "Basic YWRtaW46c3VwZXJzZWNyZXRwaXBlbGluZQ=="
}  # admin:supersecretpipeline


import os

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

    response = client.post("/generate", json=payload, headers=auth_headers)

    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]


@patch.dict(os.environ, {"API_PASSWORD": "supersecretpipeline"})
def test_generate_video_endpoint_missing_payload():
    response = client.post("/generate", json={}, headers=auth_headers)

    # Missing required 'topic' field should return 422 Unprocessable Entity
    assert response.status_code == 422
