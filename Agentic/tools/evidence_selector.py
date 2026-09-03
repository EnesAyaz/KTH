import json
from pathlib import Path


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize(
    text
):

    if text is None:
        return ""

    return (
        str(text)
        .strip()
        .lower()
    )


# =========================================================
# SECTION MATCH
# =========================================================

def section_matches(
    requested_section,
    claim_sections,
):

    requested = normalize(
        requested_section
    )

    for section in claim_sections:

        candidate = normalize(
            section
        )

        if not candidate:
            continue

        # Exact match
        if requested == candidate:
            return True

        # Flexible partial match
        if requested in candidate:
            return True

        if candidate in requested:
            return True

    return False


# =========================================================
# SELECT EVIDENCE
# =========================================================

def select_evidence_for_section(
    evidence_file: Path,
    section_name: str,
    full_text_only: bool = True,
):
    """
    Select scientific claims relevant to one review-paper
    section.

    Returns a dictionary suitable for passing directly to
    the Writer Agent.
    """

    data = json.loads(
        evidence_file.read_text(
            encoding="utf-8"
        )
    )

    result = {
        "section": section_name,
        "papers": [],
    }

    for paper in data.get(
        "papers",
        []
    ):

        selected_claims = []

        for claim in paper.get(
            "claims",
            []
        ):

            if full_text_only:

                if (
                    claim.get(
                        "verification_level"
                    )
                    != "FULL_TEXT_VERIFIED"
                ):

                    continue

            relevant_sections = (
                claim.get(
                    "relevant_sections",
                    []
                )
            )

            if section_matches(
                section_name,
                relevant_sections,
            ):

                selected_claims.append(
                    claim
                )

        if selected_claims:

            result["papers"].append(
                {
                    "citation_key":
                        paper.get(
                            "citation_key"
                        ),

                    "title":
                        paper.get(
                            "title"
                        ),

                    "claims":
                        selected_claims,
                }
            )

    return result


# =========================================================
# CLAIM COUNT
# =========================================================

def count_claims(
    evidence_database
):

    return sum(
        len(
            paper.get(
                "claims",
                []
            )
        )
        for paper in evidence_database.get(
            "papers",
            []
        )
    )


# =========================================================
# CITATION COUNT
# =========================================================

def count_sources(
    evidence_database
):

    return len(
        evidence_database.get(
            "papers",
            []
        )
    )