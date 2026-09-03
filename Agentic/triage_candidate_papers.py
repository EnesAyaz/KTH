import json
import re
from pathlib import Path


# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

DATA_DIR = (
    ROOT_DIR
    / "data"
)

OUTPUT_DIR = (
    ROOT_DIR
    / "output"
)

CANDIDATES_FILE = (
    DATA_DIR
    / "candidate_papers.json"
)

EXISTING_PAPERS_FILE = (
    DATA_DIR
    / "papers.json"
)

TRIAGE_JSON_FILE = (
    DATA_DIR
    / "candidate_triage.json"
)

TRIAGE_REPORT_FILE = (
    OUTPUT_DIR
    / "candidate_triage.md"
)


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# NORMALIZATION
# =========================================================

def normalize_doi(doi):
    """
    Normalize DOI strings so that:

    https://doi.org/10.xxxx/abc
    10.xxxx/abc

    are treated as the same DOI.
    """

    if not doi:
        return None

    doi = str(
        doi
    ).strip().lower()

    doi = doi.replace(
        "https://doi.org/",
        ""
    )

    doi = doi.replace(
        "http://doi.org/",
        ""
    )

    doi = doi.replace(
        "doi:",
        ""
    )

    return doi.strip()


def normalize_title(title):
    """
    Normalize titles for duplicate comparison.
    """

    if not title:
        return ""

    title = str(
        title
    ).lower()

    # Remove punctuation.
    title = re.sub(
        r"[^a-z0-9\s]",
        " ",
        title,
    )

    # Collapse whitespace.
    title = re.sub(
        r"\s+",
        " ",
        title,
    )

    return title.strip()


# =========================================================
# LOAD JSON
# =========================================================

def load_json(path, default):

    if not path.exists():
        return default

    try:

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except json.JSONDecodeError:

        return default


# =========================================================
# GET PAPER LIST
# =========================================================

def extract_existing_papers(data):
    """
    Support both:

    {
        "papers": [...]
    }

    and:

    [...]
    """

    if isinstance(
        data,
        list,
    ):
        return data

    if isinstance(
        data,
        dict,
    ):
        return data.get(
            "papers",
            []
        )

    return []


# =========================================================
# BUILD EXISTING DATABASE LOOKUPS
# =========================================================

def build_existing_lookup(
    existing_papers
):

    doi_lookup = {}

    title_lookup = {}

    for paper in existing_papers:

        doi = normalize_doi(
            paper.get(
                "doi"
            )
        )

        title = normalize_title(
            paper.get(
                "title"
            )
        )

        if doi:

            doi_lookup[
                doi
            ] = paper

        if title:

            title_lookup[
                title
            ] = paper

    return (
        doi_lookup,
        title_lookup,
    )


# =========================================================
# DUPLICATE CHECK
# =========================================================

def find_duplicate(
    candidate,
    doi_lookup,
    title_lookup,
):

    candidate_doi = normalize_doi(
        candidate.get(
            "doi"
        )
    )

    candidate_title = normalize_title(
        candidate.get(
            "title"
        )
    )

    # -----------------------------------------------------
    # DOI MATCH
    # -----------------------------------------------------

    if (
        candidate_doi
        and candidate_doi in doi_lookup
    ):

        existing = (
            doi_lookup[
                candidate_doi
            ]
        )

        return {
            "is_duplicate": True,
            "duplicate_reason": "DOI match",
            "existing_title":
                existing.get(
                    "title"
                ),
            "existing_citation_key":
                existing.get(
                    "citation_key"
                ),
        }

    # -----------------------------------------------------
    # EXACT NORMALIZED TITLE MATCH
    # -----------------------------------------------------

    if (
        candidate_title
        and candidate_title in title_lookup
    ):

        existing = (
            title_lookup[
                candidate_title
            ]
        )

        return {
            "is_duplicate": True,
            "duplicate_reason":
                "Normalized title match",
            "existing_title":
                existing.get(
                    "title"
                ),
            "existing_citation_key":
                existing.get(
                    "citation_key"
                ),
        }

    return {
        "is_duplicate": False,
        "duplicate_reason": None,
        "existing_title": None,
        "existing_citation_key": None,
    }


# =========================================================
# CANDIDATE SCORING
# =========================================================

def score_candidate(
    candidate
):
    """
    Assign a deterministic priority score.

    This score does not judge paper quality.

    It ranks papers based on how useful they may be for
    filling the project's current evidence gaps.
    """

    score = 0

    reasons = []

    title = (
        candidate.get(
            "title",
            ""
        )
        or ""
    ).lower()

    target_topics = [
        str(item).lower()

        for item in candidate.get(
            "target_topics",
            []
        )
    ]

    useful_fields = [
        str(item).lower()

        for item in candidate.get(
            "expected_useful_fields",
            []
        )
    ]

    experimental = (
        candidate.get(
            "experimental_relevance",
            ""
        )
        or ""
    ).lower()

    full_text_value = (
        candidate.get(
            "likely_full_text_value",
            ""
        )
        or ""
    ).lower()

    # -----------------------------------------------------
    # DIRECT SPB RELEVANCE
    # -----------------------------------------------------

    direct_spb_terms = [
        "stacked polyphase",
        "stacked polyphase bridge",
        "stacked polyphase bridges",
    ]

    if any(
        term in title
        for term in direct_spb_terms
    ):

        score += 6

        reasons.append(
            "Direct SPB paper"
        )

    # -----------------------------------------------------
    # INTEGRATED MODULAR DRIVE
    # -----------------------------------------------------

    if (
        "integrated modular motor drive"
        in title
        or
        "integrated motor drive"
        in title
    ):

        score += 3

        reasons.append(
            "Direct integrated-drive relevance"
        )

    # -----------------------------------------------------
    # TARGET TOPICS
    # -----------------------------------------------------

    for topic in target_topics:

        if (
            "stacked polyphase"
            in topic
        ):

            score += 3

        elif (
            "experimental"
            in topic
        ):

            score += 2

        elif (
            "efficiency"
            in topic
        ):

            score += 2

        elif (
            "power density"
            in topic
        ):

            score += 2

        elif (
            "semiconductor"
            in topic
        ):

            score += 1

        elif (
            "integrated modular"
            in topic
        ):

            score += 2

    # -----------------------------------------------------
    # QUANTITATIVE FIELDS
    # -----------------------------------------------------

    quantitative_priority = {
        "rated_power_kw": 2,
        "peak_power_kw": 1,
        "dc_link_voltage_v": 2,
        "cell_voltage_v": 2,
        "number_of_cells": 2,
        "number_of_phases": 1,
        "semiconductor_voltage_rating_v": 2,
        "semiconductor_current_rating_a": 1,
        "switching_frequency_khz": 2,
        "efficiency_percent": 3,
        "power_density_kw_per_l": 3,
    }

    quantitative_score = 0

    for field in useful_fields:

        value = (
            quantitative_priority.get(
                field,
                0,
            )
        )

        quantitative_score += value

    # Cap this contribution so a speculative long list
    # cannot dominate the ranking.
    quantitative_score = min(
        quantitative_score,
        12,
    )

    score += quantitative_score

    if quantitative_score >= 8:

        reasons.append(
            "Potentially rich quantitative dataset"
        )

    # -----------------------------------------------------
    # EXPERIMENTAL RELEVANCE
    # -----------------------------------------------------

    if "strong" in experimental:

        score += 5

        reasons.append(
            "Strong experimental relevance"
        )

    elif (
        "experimental"
        in experimental
    ):

        score += 3

        reasons.append(
            "Potential experimental validation"
        )

    # -----------------------------------------------------
    # EXPECTED FULL-TEXT VALUE
    # -----------------------------------------------------

    if (
        "very high"
        in full_text_value
    ):

        score += 4

        reasons.append(
            "Very high expected full-text value"
        )

    elif (
        "high"
        in full_text_value
    ):

        score += 2

        reasons.append(
            "High expected full-text value"
        )

    # -----------------------------------------------------
    # DOI
    # -----------------------------------------------------

    if candidate.get(
        "doi"
    ):

        score += 1

        reasons.append(
            "DOI available"
        )

    return (
        score,
        reasons,
    )


# =========================================================
# PRIORITY CLASSIFICATION
# =========================================================

def priority_from_score(
    score
):

    if score >= 28:
        return "P1 - VERY HIGH"

    if score >= 20:
        return "P2 - HIGH"

    if score >= 12:
        return "P3 - MEDIUM"

    return "P4 - LOW"


# =========================================================
# TRIAGE
# =========================================================

def triage_candidates(
    candidates,
    existing_papers,
):

    (
        doi_lookup,
        title_lookup,
    ) = build_existing_lookup(
        existing_papers
    )

    results = []

    for candidate in candidates:

        duplicate = (
            find_duplicate(
                candidate,
                doi_lookup,
                title_lookup,
            )
        )

        score, reasons = (
            score_candidate(
                candidate
            )
        )

        if duplicate[
            "is_duplicate"
        ]:

            download_recommendation = (
                "SKIP - ALREADY IN PROJECT"
            )

        else:

            priority = (
                priority_from_score(
                    score
                )
            )

            if priority.startswith(
                "P1"
            ):

                download_recommendation = (
                    "DOWNLOAD FIRST"
                )

            elif priority.startswith(
                "P2"
            ):

                download_recommendation = (
                    "DOWNLOAD"
                )

            elif priority.startswith(
                "P3"
            ):

                download_recommendation = (
                    "OPTIONAL / SECOND ROUND"
                )

            else:

                download_recommendation = (
                    "LOW PRIORITY"
                )

        result = {
            **candidate,

            "triage_score":
                score,

            "priority":
                priority_from_score(
                    score
                ),

            "triage_reasons":
                reasons,

            "is_duplicate":
                duplicate[
                    "is_duplicate"
                ],

            "duplicate_reason":
                duplicate[
                    "duplicate_reason"
                ],

            "existing_title":
                duplicate[
                    "existing_title"
                ],

            "existing_citation_key":
                duplicate[
                    "existing_citation_key"
                ],

            "download_recommendation":
                download_recommendation,
        }

        results.append(
            result
        )

    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    results.sort(
        key=lambda item: (
            item[
                "is_duplicate"
            ],
            -item[
                "triage_score"
            ],
        )
    )

    return results


# =========================================================
# MARKDOWN REPORT
# =========================================================

def create_markdown_report(
    results
):

    lines = []

    lines.append(
        "# Candidate Paper Triage"
    )

    lines.append("")

    lines.append(
        "This report ranks candidate publications before "
        "PDF acquisition and full-text evidence extraction."
    )

    lines.append("")

    lines.append(
        "The score is a workflow priority only. It does not "
        "represent scientific quality."
    )

    lines.append("")

    # -----------------------------------------------------
    # SUMMARY TABLE
    # -----------------------------------------------------

    lines.append(
        "## Summary"
    )

    lines.append("")

    lines.append(
        "| Rank | Priority | Score | Recommendation | Paper |"
    )

    lines.append(
        "|---:|---|---:|---|---|"
    )

    rank = 1

    for item in results:

        title = (
            item.get(
                "title",
                "Unknown"
            )
            .replace(
                "|",
                "\\|"
            )
        )

        lines.append(
            f"| {rank} "
            f"| {item['priority']} "
            f"| {item['triage_score']} "
            f"| {item['download_recommendation']} "
            f"| {title} |"
        )

        rank += 1

    lines.append("")

    # -----------------------------------------------------
    # DETAILS
    # -----------------------------------------------------

    lines.append(
        "## Detailed Triage"
    )

    lines.append("")

    for index, item in enumerate(
        results,
        start=1,
    ):

        lines.append(
            f"### {index}. "
            f"{item.get('title')}"
        )

        lines.append("")

        lines.append(
            f"- Priority: "
            f"**{item['priority']}**"
        )

        lines.append(
            f"- Score: "
            f"**{item['triage_score']}**"
        )

        lines.append(
            f"- Recommendation: "
            f"**{item['download_recommendation']}**"
        )

        doi = item.get(
            "doi"
        )

        if doi:

            lines.append(
                f"- DOI: `{doi}`"
            )

        if item[
            "is_duplicate"
        ]:

            lines.append(
                "- Duplicate: **YES**"
            )

            lines.append(
                f"- Duplicate reason: "
                f"{item['duplicate_reason']}"
            )

            if item[
                "existing_citation_key"
            ]:

                lines.append(
                    f"- Existing citation key: "
                    f"`{item['existing_citation_key']}`"
                )

        else:

            lines.append(
                "- Duplicate: No"
            )

        lines.append("")

        if item[
            "triage_reasons"
        ]:

            lines.append(
                "Reasons:"
            )

            lines.append("")

            for reason in item[
                "triage_reasons"
            ]:

                lines.append(
                    f"- {reason}"
                )

        lines.append("")

    TRIAGE_REPORT_FILE.write_text(
        "\n".join(
            lines
        ),
        encoding="utf-8",
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print(
        "========================================"
    )

    print(
        "CANDIDATE PAPER TRIAGE"
    )

    print(
        "========================================"
    )

    print()

    # -----------------------------------------------------
    # CHECK CANDIDATES
    # -----------------------------------------------------

    if not CANDIDATES_FILE.exists():

        print(
            "candidate_papers.json does not exist."
        )

        print()

        print(
            "Run:"
        )

        print()

        print(
            "python run_targeted_literature_search.py"
        )

        return

    # -----------------------------------------------------
    # LOAD
    # -----------------------------------------------------

    candidate_database = (
        load_json(
            CANDIDATES_FILE,
            {
                "candidates": []
            },
        )
    )

    existing_database = (
        load_json(
            EXISTING_PAPERS_FILE,
            {
                "papers": []
            },
        )
    )

    candidates = (
        candidate_database.get(
            "candidates",
            []
        )
    )

    existing_papers = (
        extract_existing_papers(
            existing_database
        )
    )

    # -----------------------------------------------------
    # TRIAGE
    # -----------------------------------------------------

    results = (
        triage_candidates(
            candidates,
            existing_papers,
        )
    )

    # -----------------------------------------------------
    # SAVE JSON
    # -----------------------------------------------------

    output_data = {
        "candidate_count":
            len(results),

        "existing_paper_count":
            len(existing_papers),

        "candidates":
            results,
    }

    TRIAGE_JSON_FILE.write_text(
        json.dumps(
            output_data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # SAVE MARKDOWN
    # -----------------------------------------------------

    create_markdown_report(
        results
    )

    # -----------------------------------------------------
    # TERMINAL SUMMARY
    # -----------------------------------------------------

    print(
        f"Candidates analyzed: "
        f"{len(results)}"
    )

    print(
        f"Existing papers: "
        f"{len(existing_papers)}"
    )

    print()

    print(
        "DOWNLOAD PRIORITY"
    )

    print(
        "----------------------------------------"
    )

    for index, item in enumerate(
        results,
        start=1,
    ):

        print(
            f"{index:2}. "
            f"[{item['priority']}] "
            f"{item['title']}"
        )

        print(
            f"    "
            f"{item['download_recommendation']}"
        )

        if item[
            "is_duplicate"
        ]:

            print(
                f"    Duplicate: "
                f"{item['duplicate_reason']}"
            )

        print()

    print(
        "Files created:"
    )

    print()

    print(
        TRIAGE_JSON_FILE
    )

    print(
        TRIAGE_REPORT_FILE
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "No papers.json entries were modified."
    )

    print(
        "No candidate was treated as verified evidence."
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()