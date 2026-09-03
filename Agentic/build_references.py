import json
import re
from pathlib import Path

import requests


# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

PAPERS_FILE = (
    ROOT_DIR
    / "data"
    / "papers.json"
)

OUTPUT_DIR = (
    ROOT_DIR
    / "output"
)

BIB_FILE = (
    OUTPUT_DIR
    / "references.bib"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# DOWNLOAD BIBTEX FROM DOI
# =========================================================

def get_bibtex(
    doi: str
) -> str | None:

    doi = doi.strip()

    doi = doi.replace(
        "https://doi.org/",
        ""
    )

    url = (
        f"https://doi.org/{doi}"
    )

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

        return response.text.strip()

    except requests.RequestException as error:

        print(
            f"Failed DOI: {doi}"
        )

        print(
            error
        )

        return None


# =========================================================
# NORMALIZE CITATION KEY
# =========================================================

def replace_bibtex_key(
    bibtex: str,
    citation_key: str,
) -> str:
    """
    Replace the citation key returned by DOI metadata with
    the citation key stored in papers.json.

    Example:

    @article{jin_2017_abc,

    becomes:

    @article{Jin2017,
    """

    pattern = (
        r"^(@[A-Za-z]+\s*\{\s*)"
        r"[^,]+"
        r"(,)"
    )

    replacement = (
        rf"\1{citation_key}\2"
    )

    return re.sub(
        pattern,
        replacement,
        bibtex,
        count=1,
        flags=re.MULTILINE,
    )


# =========================================================
# MAIN
# =========================================================

def main():

    if not PAPERS_FILE.exists():

        print(
            f"papers.json not found: "
            f"{PAPERS_FILE}"
        )

        return

    database = json.loads(
        PAPERS_FILE.read_text(
            encoding="utf-8"
        )
    )

    papers = database.get(
        "papers",
        []
    )

    entries = []

    used_keys = set()

    print()
    print("==============================")
    print("BUILDING REFERENCES")
    print("==============================")
    print()

    for paper in papers:

        doi = paper.get("doi")

        citation_key = paper.get(
            "citation_key"
        )

        if not doi:

            print(
                "Skipping paper without DOI:"
            )

            print(
                paper.get("title")
            )

            print()

            continue

        if not citation_key:

            print(
                "Skipping paper without citation key:"
            )

            print(
                paper.get("title")
            )

            print()

            continue

        if citation_key in used_keys:

            print(
                f"Duplicate citation key: "
                f"{citation_key}"
            )

            continue

        print(
            f"Fetching: {citation_key}"
        )

        bibtex = get_bibtex(
            doi
        )

        if bibtex is None:
            continue

        normalized = replace_bibtex_key(
            bibtex,
            citation_key,
        )

        entries.append(
            normalized
        )

        used_keys.add(
            citation_key
        )

    BIB_FILE.write_text(
        "\n\n".join(entries)
        + "\n",
        encoding="utf-8",
    )

    print()
    print("==============================")
    print("REFERENCES COMPLETE")
    print("==============================")
    print()
    print(
        f"{len(entries)} BibTeX entries saved."
    )
    print()
    print(BIB_FILE)
    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()