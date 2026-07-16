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


def test_sanitize_topic_boundaries():
    from src.worker import sanitize_topic

    # Test valid input
    assert sanitize_topic("Hello World!") == "hello_world"

    # Test empty input
    assert sanitize_topic("") == "default_project"
    assert sanitize_topic("   ") == "default_project"

    # Test completely invalid input
    assert sanitize_topic("???@@@###") == "default_project"
    assert sanitize_topic(None) == "default_project"

    # Test length boundaries
    long_topic = "A" * 100
    sanitized = sanitize_topic(long_topic)
    assert len(sanitized) == 50
    assert sanitized == "a" * 50

def test_async_queue_wrapper_exception_handling():
    from src.worker import async_queue_wrapper

    @async_queue_wrapper
    def mock_task_success():
        return {"status": "success"}

    @async_queue_wrapper
    def mock_task_fail():
        raise ValueError("Simulated Exception")

    @async_queue_wrapper
    def mock_task_timeout():
        from celery.exceptions import SoftTimeLimitExceeded
        raise SoftTimeLimitExceeded("Timeout")

    assert mock_task_success() == {"status": "success"}

    res_fail = mock_task_fail()
    assert res_fail["status"] == "error"
    assert "Simulated Exception" in res_fail["message"]

    res_timeout = mock_task_timeout()
    assert res_timeout["status"] == "error"
    assert "exceeded soft time limit" in res_timeout["message"]
