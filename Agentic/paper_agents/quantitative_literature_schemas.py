from typing import Literal

from pydantic import BaseModel, Field


# =========================================================
# ALLOWED STATUS TYPES
# =========================================================

RelevanceLevel = Literal[
    "HIGH",
    "MEDIUM",
    "LOW",
    "UNKNOWN",
]

AccessLikelihood = Literal[
    "HIGH",
    "MEDIUM",
    "LOW",
    "UNKNOWN",
]


# =========================================================
# QUANTITATIVE PAPER CANDIDATE
# =========================================================

class QuantitativePaperCandidate(BaseModel):
    """
    One publication identified as potentially useful for
    filling quantitative gaps in the comparison database.

    IMPORTANT:
    expected_quantitative_fields indicates only that the
    paper appears promising for those fields.

    It does NOT mean those values have been scientifically
    verified from the full text.
    """

    title: str

    authors: list[str] = Field(
        default_factory=list
    )

    year: int | None = None

    journal_or_venue: str | None = None

    doi: str | None = None

    url: str | None = None

    publication_type: str | None = None

    matched_topic_ids: list[str] = Field(
        default_factory=list
    )

    expected_quantitative_fields: list[str] = Field(
        default_factory=list
    )

    expected_quantitative_pairs: list[str] = Field(
        default_factory=list
    )

    experimental_relevance: RelevanceLevel = (
        "UNKNOWN"
    )

    quantitative_relevance: RelevanceLevel = (
        "UNKNOWN"
    )

    full_text_access_likelihood: AccessLikelihood = (
        "UNKNOWN"
    )

    selection_rationale: str

    verification_status: Literal[
        "CANDIDATE_METADATA_ONLY"
    ] = "CANDIDATE_METADATA_ONLY"


# =========================================================
# COMPLETE SEARCH RESULT
# =========================================================

class QuantitativeLiteratureResult(BaseModel):

    search_summary: str

    candidates: list[
        QuantitativePaperCandidate
    ] = Field(
        default_factory=list
    )

    unresolved_targets: list[str] = Field(
        default_factory=list
    )