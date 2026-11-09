import logging
import urllib.request
import urllib.parse
import json

logger = logging.getLogger(__name__)


def fetch_wikipedia_summary(query: str, lang: str = "en") -> str:
    """
    Fetches the plain text summary for a given topic from the Wikipedia REST API.

    Args:
        query (str): The topic to search for on Wikipedia.
        lang (str): The language code for the Wikipedia subdomain.

    Returns:
        str: The extracted plain text summary.

    Raises:
        ValueError: If the query is empty or the API returns an error.
        urllib.error.URLError: If the network request fails.
    """
    if not query:
        raise ValueError("Query string cannot be empty.")

    # Format the query for the Wikipedia API URL
    formatted_query = urllib.parse.quote(query)

    # We use the Page Summary REST API endpoint
    # https://en.wikipedia.org/api/rest_v1/#/Page%20content/get_page_summary__title_
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{formatted_query}"

    logger.info(f"Fetching Wikipedia summary for '{query}' from {url}")

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "AutomatedVideoPipeline/0.1.0 (https://github.com/robertpelloni)"
        },
    )

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))

            # The API returns 'extract' which is the plain-text summary
            if "extract" in data:
                logger.debug("Successfully extracted Wikipedia summary.")
                return data["extract"]
            else:
                logger.error(
                    "The Wikipedia API response did not contain an 'extract' field."
                )
                raise ValueError("No text extract found for the given query.")

    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ValueError(f"Wikipedia article not found for query: '{query}'")
        else:
            raise ValueError(f"Wikipedia API returned HTTP {e.code}: {e.reason}")


def fetch_wikipedia_sections(title: str, lang: str = "en") -> list:
    """
    Fetches the structural outline and section headers for a given Wikipedia article
    using the Wikipedia Action API.

    Args:
        title (str): Title of the Wikipedia page.
        lang (str): Language code.

    Returns:
        list: List of dictionaries with section 'line' (title) and 'number'.
    """
    if not title:
        raise ValueError("Title cannot be empty.")

    params = urllib.parse.urlencode(
        {"action": "parse", "page": title, "prop": "sections", "format": "json"}
    )
    url = f"https://{lang}.wikipedia.org/w/api.php?{params}"

    logger.info(f"Fetching Wikipedia sections for '{title}' from {url}")

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "AutomatedVideoPipeline/0.4.0 (https://github.com/robertpelloni)"
        },
    )

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            if "parse" in data and "sections" in data["parse"]:
                return data["parse"]["sections"]
            return []
    except Exception as e:
        logger.warning(f"Could not fetch Wikipedia sections for '{title}': {e}")
        return []


def ingest_topic_content(query: str, lang: str = "en") -> dict:
    """
    Orchestrates multi-source content ingestion: retrieves the lead summary
    and structural section outlines to provide comprehensive context for video scripting.

    Args:
        query (str): The subject query.
        lang (str): Language code.

    Returns:
        dict: A structured knowledge object containing 'title', 'summary', and 'sections'.
    """
    summary = fetch_wikipedia_summary(query, lang=lang)
    sections = fetch_wikipedia_sections(query, lang=lang)

    section_titles = [
        sec.get("line")
        for sec in sections
        if sec.get("line") not in ("See also", "References", "External links")
    ]

    return {
        "title": query,
        "summary": summary,
        "sections": section_titles,
        "combined_text": (
            f"{summary} Key topics explored include: {', '.join(section_titles[:4])}."
            if section_titles
            else summary
        ),
    }
