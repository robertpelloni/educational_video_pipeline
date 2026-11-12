import pytest
import json
import urllib.error
from unittest.mock import patch, MagicMock
from src.ingestion_engine import (
    fetch_wikipedia_summary,
    fetch_wikipedia_sections,
    ingest_topic_content,
)


@patch("src.ingestion_engine.urllib.request.urlopen")
def test_fetch_wikipedia_summary_success(mock_urlopen):
    # Mock a successful JSON response containing the extract
    mock_response = MagicMock()
    mock_data = json.dumps({"extract": "The heart is a muscular organ."}).encode(
        "utf-8"
    )
    mock_response.read.return_value = mock_data
    mock_urlopen.return_value.__enter__.return_value = mock_response

    result = fetch_wikipedia_summary("Heart")

    assert result == "The heart is a muscular organ."
    mock_urlopen.assert_called_once()

    # Check if the correct URL was called
    request_url = mock_urlopen.call_args[0][0].full_url
    assert request_url == "https://en.wikipedia.org/api/rest_v1/page/summary/Heart"


def test_fetch_wikipedia_summary_empty_query():
    with pytest.raises(ValueError, match="Query string cannot be empty."):
        fetch_wikipedia_summary("")


@patch("src.ingestion_engine.urllib.request.urlopen")
def test_fetch_wikipedia_summary_not_found(mock_urlopen):
    # Simulate a 404 HTTPError for a topic that doesn't exist
    error_mock = urllib.error.HTTPError(
        url="", hdrs=None, fp=None, code=404, msg="Not Found"
    )
    mock_urlopen.side_effect = error_mock

    with pytest.raises(
        ValueError, match="Wikipedia article not found for query: 'NonExistentTopic123'"
    ):
        fetch_wikipedia_summary("NonExistentTopic123")


@patch("src.ingestion_engine.urllib.request.urlopen")
def test_fetch_wikipedia_summary_missing_extract(mock_urlopen):
    # Mock a JSON response that doesn't contain the expected 'extract' key
    mock_response = MagicMock()
    mock_data = json.dumps({"title": "Heart"}).encode("utf-8")
    mock_response.read.return_value = mock_data
    mock_urlopen.return_value.__enter__.return_value = mock_response

    with pytest.raises(ValueError, match="No text extract found for the given query."):
        fetch_wikipedia_summary("Heart")


@patch("src.ingestion_engine.urllib.request.urlopen")
def test_fetch_wikipedia_sections_success(mock_urlopen):
    mock_response = MagicMock()
    mock_data = json.dumps(
        {
            "parse": {
                "sections": [
                    {"line": "Structure", "number": "1"},
                    {"line": "Function", "number": "2"},
                    {"line": "Clinical significance", "number": "3"},
                    {"line": "References", "number": "4"},
                ]
            }
        }
    ).encode("utf-8")
    mock_response.read.return_value = mock_data
    mock_urlopen.return_value.__enter__.return_value = mock_response

    sections = fetch_wikipedia_sections("Heart")
    assert len(sections) == 4
    assert sections[0]["line"] == "Structure"


@patch("src.ingestion_engine.fetch_wikipedia_sections")
@patch("src.ingestion_engine.fetch_wikipedia_summary")
def test_ingest_topic_content_multi_source(mock_summary, mock_sections):
    mock_summary.return_value = (
        "The brain is an organ that serves as the center of the nervous system."
    )
    mock_sections.return_value = [
        {"line": "Anatomy"},
        {"line": "Physiology"},
        {"line": "Development"},
        {"line": "References"},
    ]

    result = ingest_topic_content("Brain")
    assert result["title"] == "Brain"
    assert "center of the nervous system" in result["summary"]
    assert "Anatomy" in result["sections"]
    assert "Physiology" in result["sections"]
    assert "References" not in result["sections"]
    assert (
        "Key topics explored include: Anatomy, Physiology, Development"
        in result["combined_text"]
    )
