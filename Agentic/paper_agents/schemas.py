from typing import Literal

from pydantic import BaseModel, Field


# =========================================================
# LITERATURE DATABASE
# =========================================================


class PaperRecord(BaseModel):
    """
    Bibliographic and high-level information for one
    publication.
    """

    title: str

    authors: list[str]

    year: int | None = None

    doi: str | None = None

    journal: str | None = None

    citation_key: str | None = None

    main_contribution: str

    relevant_sections: list[str]

    quantitative_results: list[str] = Field(
        default_factory=list
    )

    limitations: list[str] = Field(
        default_factory=list
    )

    verification_status: str


class LiteratureDatabase(BaseModel):
    """
    Collection of publications identified by the
    Literature Agent.
    """

    search_topic: str

    papers: list[PaperRecord]


# =========================================================
# SCIENTIFIC EVIDENCE
# =========================================================


class EvidenceClaim(BaseModel):
    """
    One scientific claim extracted from a publication.
    """

    claim_id: str

    statement: str

    citation_key: str

    source_title: str

    page_number: int | None = None

    evidence_type: Literal[
        "definition",
        "method",
        "experimental_result",
        "numerical_result",
        "comparison",
        "limitation",
        "conclusion",
    ]

    relevant_sections: list[str] = Field(
        default_factory=list
    )

    numerical_values: list[str] = Field(
        default_factory=list
    )

    supporting_excerpt: str | None = None

    verification_level: Literal[
        "FULL_TEXT_VERIFIED",
        "ABSTRACT_ONLY",
        "METADATA_ONLY",
    ]

    confidence: Literal[
        "high",
        "medium",
        "low",
    ]


class PaperEvidence(BaseModel):
    """
    Scientific evidence extracted from one publication.
    """

    citation_key: str

    title: str

    pdf_filename: str | None = None

    claims: list[EvidenceClaim]

    unresolved_questions: list[str] = Field(
        default_factory=list
    )


class EvidenceDatabase(BaseModel):
    """
    Complete scientific evidence database.
    """

    papers: list[PaperEvidence]


# =========================================================
# COMPARISON DATABASE
# =========================================================


class ComparisonRecord(BaseModel):
    """
    Standardized comparison record for one reviewed
    converter / machine demonstration.

    Fields may be None when the source does not report them.
    """

    citation_key: str

    title: str

    topology: str | None = None

    rated_power_kw: float | None = None

    peak_power_kw: float | None = None

    dc_link_voltage_v: float | None = None

    cell_voltage_v: float | None = None

    number_of_cells: int | None = None

    number_of_phases: int | None = None

    semiconductor_technology: str | None = None

    semiconductor_voltage_rating_v: float | None = None

    semiconductor_current_rating_a: float | None = None

    switching_frequency_khz: float | None = None

    efficiency_percent: float | None = None

    power_density_kw_per_l: float | None = None

    machine_type: str | None = None

    winding_configuration: str | None = None

    modulation_method: str | None = None

    cooling_method: str | None = None

    balancing_requirement: str | None = None

    common_mode_information: str | None = None

    fault_tolerance: str | None = None

    post_fault_capability: str | None = None

    experimental_level: str | None = None

    test_conditions: str | None = None

    main_advantages: list[str] = Field(
        default_factory=list
    )

    main_limitations: list[str] = Field(
        default_factory=list
    )

    evidence_claim_ids: list[str] = Field(
        default_factory=list
    )

    missing_information: list[str] = Field(
        default_factory=list
    )


class ComparisonDatabase(BaseModel):
    """
    Standardized comparison records derived ONLY from
    verified evidence.
    """

    records: list[ComparisonRecord]