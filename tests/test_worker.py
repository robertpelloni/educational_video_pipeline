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


@patch("src.worker.fetch_platform_analytics", return_value={"feedback_summary": None})
@patch(
    "src.worker.fetch_wikipedia_summary",
    return_value="Photosynthesis converts light to energy.",
)
@patch("src.worker.generate_script_from_text")
@patch("src.worker.generate_all_voiceovers")
@patch("src.worker.compile_video")
@patch("src.worker.os.path.exists", return_value=True)
def test_worker_style_preset_propagation(
    mock_exists,
    mock_compile,
    mock_voiceovers,
    mock_gen_script,
    mock_wiki,
    mock_analytics,
):
    mock_gen_script.return_value = {
        "project_id": "biology_101",
        "canvas_format": ["landscape"],
        "background_music": "assets/music/default_background.mp3",
        "global_music_volume_db": -18.0,
        "scenes": [],
        "youtube_metadata": {
            "title": "Title",
            "description": "Desc",
            "tags": [],
            "category_id": "27",
        },
    }

    result = run_pipeline_task(
        "Biology 101", skip_upload=True, style_preset="microscopic_render"
    )

    assert result["status"] == "success"
    mock_gen_script.assert_called_once_with(
        "Photosynthesis converts light to energy.",
        project_id="biology_101",
        analytics_feedback=None,
        style_preset="microscopic_render",
    )
