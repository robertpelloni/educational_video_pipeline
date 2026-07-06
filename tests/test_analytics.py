import pytest
from src.analytics_engine import fetch_platform_analytics

def test_fetch_platform_analytics():
    project_id = "test_project_123"
    result = fetch_platform_analytics(project_id)

    assert "metrics" in result
    assert "youtube" in result["metrics"]
    assert "tiktok" in result["metrics"]

    assert "feedback_summary" in result
    assert isinstance(result["feedback_summary"], str)
    assert len(result["feedback_summary"]) > 0
