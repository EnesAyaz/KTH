import json
import re
from pathlib import Path


# =========================================================
# LOAD ALLOWED CITATION KEYS
# =========================================================

def get_allowed_citations(
    evidence_file: Path
) -> set[str]:
    """
    Extract citation keys from FULL_TEXT_VERIFIED evidence.
    """

    data = json.loads(
        evidence_file.read_text(
            encoding="utf-8"
        )
    )

    allowed = set()

    for paper in data.get(
        "papers",
        []
    ):

        for claim in paper.get(
            "claims",
            []
        ):

            verification = claim.get(
                "verification_level"
            )

            if verification != "FULL_TEXT_VERIFIED":
                continue

            citation_key = claim.get(
                "citation_key"
            )

            if citation_key:
                allowed.add(
                    citation_key.strip()
                )

    return allowed


# =========================================================
# EXTRACT CITATIONS FROM LATEX
# =========================================================

def extract_latex_citations(
    latex_text: str
) -> set[str]:
    """
    Find citation keys used in \\cite{...}.
    """

    pattern = r"\\cite\{([^}]+)\}"

    matches = re.findall(
        pattern,
        latex_text
    )

    citations = set()

    for match in matches:

        keys = match.split(",")

        for key in keys:

            clean_key = key.strip()

            if clean_key:
                citations.add(
                    clean_key
                )

    return citations


# =========================================================
# CHECK CITATIONS
# =========================================================

def check_citations(
    latex_file: Path,
    evidence_file: Path,
) -> dict:
    """
    Compare citations used in a LaTeX file with citation
    keys available in verified evidence.
    """

    latex_text = latex_file.read_text(
        encoding="utf-8"
    )

    allowed = get_allowed_citations(
        evidence_file
    )

    used = extract_latex_citations(
        latex_text
    )

    invalid = used - allowed

    unused = allowed - used

    return {
        "allowed": allowed,
        "used": used,
        "invalid": invalid,
        "unused": unused,
    }