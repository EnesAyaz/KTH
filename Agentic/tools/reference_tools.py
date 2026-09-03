import requests

from agents.decorators import tool


@tool
def doi_to_bibtex(doi: str) -> str:
    """
    Retrieve BibTeX metadata from a DOI.

    Args:
        doi: Digital Object Identifier of a publication.
    """

    doi = doi.strip()

    if doi.startswith("https://doi.org/"):
        doi = doi.replace(
            "https://doi.org/",
            ""
        )

    url = f"https://doi.org/{doi}"

    headers = {
        "Accept":
            "application/x-bibtex"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

    except requests.RequestException as error:

        return (
            "BIBTEX_RETRIEVAL_FAILED: "
            f"{error}"
        )

    return response.text