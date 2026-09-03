import json
import requests

from agents.decorators import tool


@tool
def crossref_search(
    query: str,
    rows: int = 10
) -> str:
    """
    Search Crossref for academic publications.

    Args:
        query: Search terms, research topic, or paper title.
        rows: Maximum number of search results.
    """

    url = "https://api.crossref.org/works"

    params = {
        "query.bibliographic": query,
        "rows": rows,
        "select": (
            "DOI,title,author,published,"
            "container-title,type,URL"
        ),
    }

    headers = {
        "User-Agent":
            "AgenticReviewPaper/1.0 "
            "(academic literature research)"
    }

    try:

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

    except requests.RequestException as error:

        return json.dumps(
            {
                "error": str(error)
            }
        )

    items = response.json()["message"]["items"]

    results = []

    for item in items:

        # --------------------------
        # AUTHORS
        # --------------------------

        authors = []

        for author in item.get("author", []):

            given = author.get("given", "")
            family = author.get("family", "")

            full_name = (
                f"{given} {family}"
            ).strip()

            if full_name:
                authors.append(full_name)

        # --------------------------
        # YEAR
        # --------------------------

        year = None

        published = item.get(
            "published",
            {}
        )

        date_parts = published.get(
            "date-parts",
            []
        )

        if date_parts and date_parts[0]:
            year = date_parts[0][0]

        # --------------------------
        # TITLE
        # --------------------------

        titles = item.get("title", [])

        title = (
            titles[0]
            if titles
            else ""
        )

        # --------------------------
        # JOURNAL
        # --------------------------

        containers = item.get(
            "container-title",
            []
        )

        journal = (
            containers[0]
            if containers
            else ""
        )

        # --------------------------
        # RECORD
        # --------------------------

        results.append(
            {
                "title": title,
                "authors": authors,
                "year": year,
                "doi": item.get("DOI"),
                "journal": journal,
                "type": item.get("type"),
                "url": item.get("URL"),
            }
        )

    return json.dumps(
        results,
        ensure_ascii=False,
        indent=2,
    )