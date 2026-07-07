from unittest.mock import patch
from src.worker import run_pipeline_task
from celery.exceptions import SoftTimeLimitExceeded


@patch("src.worker.fetch_wikipedia_summary")
def test_worker_timeout_handling(mock_fetch):
    # Simulate a timeout happening during the ingestion phase
    mock_fetch.side_effect = SoftTimeLimitExceeded()

    result = run_pipeline_task("Black hole", skip_upload=True)

    assert result["status"] == "error"
    assert "exceeded soft time limit" in result["message"]
