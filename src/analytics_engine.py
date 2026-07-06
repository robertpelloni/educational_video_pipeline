import logging
import random

logger = logging.getLogger(__name__)


def fetch_platform_analytics(project_id: str):
    """
    Simulates fetching performance analytics across different platforms for a given project.
    In a real implementation, this would query YouTube Analytics API, TikTok Graph API, etc.

    Args:
        project_id (str): The project identifier to fetch analytics for.

    Returns:
        dict: A dictionary containing simulated performance metrics and sentiment analysis.
    """
    logger.info(f"Fetching cross-platform analytics for project '{project_id}'...")

    # Simulate API latency and random performance metrics
    metrics = {
        "youtube": {
            "views": random.randint(100, 10000),
            "avg_watch_time_pct": random.uniform(0.3, 0.8),
            "audience_sentiment": random.choice(["positive", "neutral", "mixed"]),
        },
        "tiktok": {
            "views": random.randint(500, 50000),
            "completion_rate": random.uniform(0.1, 0.6),
            "audience_sentiment": random.choice(["positive", "neutral", "negative"]),
        },
    }

    # Simple heuristic to determine feedback for the LLM
    feedback_notes = []

    if metrics["youtube"]["avg_watch_time_pct"] < 0.4:
        feedback_notes.append(
            "YouTube viewers are dropping off early. Consider a stronger hook."
        )
    if metrics["tiktok"]["completion_rate"] > 0.4:
        feedback_notes.append(
            "TikTok audience is highly engaged; maintain current pacing."
        )

    if any(m["audience_sentiment"] == "negative" for m in metrics.values()):
        feedback_notes.append(
            "Sentiment is trending negative; consider adjusting tone or checking factual accuracy."
        )

    if not feedback_notes:
        feedback_notes.append(
            "Overall performance is stable. Continue current content strategy."
        )

    logger.info(f"Analytics compiled for '{project_id}': {feedback_notes}")

    return {"metrics": metrics, "feedback_summary": " ".join(feedback_notes)}
