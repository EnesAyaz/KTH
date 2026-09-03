from pydantic import BaseModel, Field


# =========================================================
# TARGETED LITERATURE CANDIDATE
# =========================================================


class TargetedPaperCandidate(BaseModel):
    """
    One candidate publication identified by the targeted
    literature search.

    IMPORTANT:
    This represents bibliographic discovery only.

    It does NOT mean that technical claims from the paper
    have been full-text verified.
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

    target_topics: list[str] = Field(
        default_factory=list
    )

    expected_useful_fields: list[str] = Field(
        default_factory=list
    )

    reason_for_selection: str

    experimental_relevance: str | None = None

    likely_full_text_value: str | None = None

    verification_status: str = (
        "CANDIDATE_METADATA_ONLY"
    )


# =========================================================
# TARGETED SEARCH RESULT
# =========================================================


class TargetedLiteratureResult(BaseModel):
    """
    Complete result from a targeted literature search.
    """

    search_summary: str

    candidates: list[
        TargetedPaperCandidate
    ] = Field(
        default_factory=list
    )

    unresolved_topics: list[str] = Field(
        default_factory=list
    )