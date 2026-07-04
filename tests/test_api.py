from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api_router import app

client = TestClient(app)

# Default valid credentials for tests
auth_headers = {
    "Authorization": "Basic YWRtaW46c3VwZXJzZWNyZXRwaXBlbGluZQ=="
}  # admin:supersecretpipeline


def test_generate_video_endpoint_unauthorized():
    payload = {"topic": "Black hole"}
    response = client.post("/generate", json=payload)
    assert response.status_code == 401


def test_generate_video_endpoint_success():
    payload = {"topic": "Black hole", "skip_upload": True}

    with patch("src.api_router.BackgroundTasks.add_task") as mock_add_task:
        response = client.post("/generate", json=payload, headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["topic"] == "Black hole"
        mock_add_task.assert_called_once()


def test_generate_video_endpoint_empty_topic():
    payload = {"topic": "   ", "skip_upload": True}

    response = client.post("/generate", json=payload, headers=auth_headers)

    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]


def test_generate_video_endpoint_missing_payload():
    response = client.post("/generate", json={}, headers=auth_headers)

    # Missing required 'topic' field should return 422 Unprocessable Entity
    assert response.status_code == 422
