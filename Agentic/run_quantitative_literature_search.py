import asyncio
import json
import re
from pathlib import Path

from dotenv import load_dotenv

from agents import Runner

from paper_agents.quantitative_literature import (
    quantitative_literature_agent,
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# PROJECT PATHS
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

TARGET_FILE = (
    DATA_DIR
    / "quantitative_literature_targets.json"
)

PAPERS_FILE = (
    DATA_DIR
    / "papers.json"
)

PREVIOUS_CANDIDATE_FILE = (
    DATA_DIR
    / "candidate_papers.json"
)

OUTPUT_JSON = (
    DATA_DIR
    / "quantitative_candidate_papers.json"
)

OUTPUT_MD = (
    OUTPUT_DIR
    / "quantitative_papers_to_review.md"
)


DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# JSON
# =========================================================

def load_json(
    path,
    default,
):

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
# NORMALIZATION
# =========================================================

def normalize_doi(
    doi,
):

    if not doi:

        return ""

    text = str(
        doi
    ).strip().lower()

    prefixes = [
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
    ]

    for prefix in prefixes:

        if text.startswith(
            prefix
        ):

            text = text[
                len(prefix):
            ]

    return text.strip()


def normalize_title(
    title,
):

    if not title:

        return ""

    text = str(
        title
    ).lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# =========================================================
# GET PAPER LIST FROM DATABASE
# =========================================================

def extract_paper_list(
    database,
):

    if isinstance(
        database,
        list,
    ):

        return database

    if isinstance(
        database,
        dict,
    ):

        return database.get(
            "papers",
            []
        )

    return []


# =========================================================
# EXISTING PUBLICATION IDENTIFIERS
# =========================================================

def build_existing_identifiers():

    existing_dois = set()

    existing_titles = set()

    existing_display = []

    # -----------------------------------------------------
    # PAPERS.JSON
    # -----------------------------------------------------

    papers_database = load_json(
        PAPERS_FILE,
        {
            "papers": []
        },
    )

    for paper in extract_paper_list(
        papers_database
    ):

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

            existing_dois.add(
                doi
            )

        if title:

            existing_titles.add(
                title
            )

        existing_display.append(
            {
                "citation_key":
                    paper.get(
                        "citation_key"
                    ),

                "title":
                    paper.get(
                        "title"
                    ),

                "doi":
                    paper.get(
                        "doi"
                    ),
            }
        )

    # -----------------------------------------------------
    # PREVIOUS CANDIDATE SEARCH
    # -----------------------------------------------------

    previous_database = load_json(
        PREVIOUS_CANDIDATE_FILE,
        {},
    )

    previous_candidates = (
        previous_database.get(
            "candidates",
            []
        )
        if isinstance(
            previous_database,
            dict,
        )
        else []
    )

    for paper in previous_candidates:

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

            existing_dois.add(
                doi
            )

        if title:

            existing_titles.add(
                title
            )

    return (
        existing_dois,
        existing_titles,
        existing_display,
    )


# =========================================================
# DETERMINISTIC DUPLICATE FILTER
# =========================================================

def remove_duplicates(
    candidates,
    existing_dois,
    existing_titles,
):

    accepted = []

    removed = []

    seen_dois = set()

    seen_titles = set()

    for candidate in candidates:

        doi = normalize_doi(
            candidate.get(
                "doi"
            )
        )

        title = normalize_title(
            candidate.get(
                "title"
            )
        )

        reason = None

        # -------------------------------------------------
        # DUPLICATE WITH EXISTING DATABASE
        # -------------------------------------------------

        if (
            doi
            and doi in existing_dois
        ):

            reason = (
                "DOI already exists in current "
                "literature/candidate database."
            )

        elif (
            title
            and title in existing_titles
        ):

            reason = (
                "Title already exists in current "
                "literature/candidate database."
            )

        # -------------------------------------------------
        # DUPLICATE WITHIN THIS SEARCH
        # -------------------------------------------------

        elif (
            doi
            and doi in seen_dois
        ):

            reason = (
                "Duplicate DOI within current search."
            )

        elif (
            title
            and title in seen_titles
        ):

            reason = (
                "Duplicate title within current search."
            )

        if reason:

            removed.append(
                {
                    "title":
                        candidate.get(
                            "title"
                        ),

                    "doi":
                        candidate.get(
                            "doi"
                        ),

                    "reason":
                        reason,
                }
            )

            continue

        # -------------------------------------------------
        # ACCEPT
        # -------------------------------------------------

        accepted.append(
            candidate
        )

        if doi:

            seen_dois.add(
                doi
            )

        if title:

            seen_titles.add(
                title
            )

    return (
        accepted,
        removed,
    )


# =========================================================
# FORMAT EXISTING PAPERS FOR PROMPT
# =========================================================

def format_existing_papers(
    existing_display,
):

    lines = []

    for paper in existing_display:

        lines.append(
            (
                f"- "
                f"{paper.get('citation_key')} | "
                f"{paper.get('title')} | "
                f"DOI: {paper.get('doi')}"
            )
        )

    return "\n".join(
        lines
    )


# =========================================================
# FORMAT FIELD GAPS
# =========================================================

def format_field_gaps(
    target_database,
):

    lines = []

    for gap in target_database.get(
        "field_gaps",
        []
    ):

        if (
            gap.get(
                "additional_records_needed",
                0,
            )
            <= 0
        ):

            continue

        lines.append(
            (
                f"- {gap.get('field')}: "
                f"{gap.get('available_records')} / "
                f"{gap.get('desired_records')} "
                f"available; need approximately +"
                f"{gap.get('additional_records_needed')}; "
                f"priority = "
                f"{gap.get('priority')}"
            )
        )

    return "\n".join(
        lines
    )


# =========================================================
# FORMAT PAIR GAPS
# =========================================================

def format_pair_gaps(
    target_database,
):

    lines = []

    for gap in target_database.get(
        "pair_gaps",
        []
    ):

        if (
            gap.get(
                "additional_paired_records_needed",
                0,
            )
            <= 0
        ):

            continue

        lines.append(
            (
                f"- {gap.get('name')}: "
                f"{gap.get('available_paired_records')} / "
                f"{gap.get('desired_paired_records')} "
                f"paired records; need approximately +"
                f"{gap.get('additional_paired_records_needed')}; "
                f"priority = "
                f"{gap.get('priority')}"
            )
        )

    return "\n".join(
        lines
    )


# =========================================================
# FORMAT SEARCH TOPICS
# =========================================================

def format_search_topics(
    target_database,
):

    lines = []

    for topic in target_database.get(
        "search_topics",
        []
    ):

        lines.append(
            (
                f"{topic.get('topic_id')} | "
                f"{topic.get('priority')} | "
                f"{topic.get('topic')}\n"
                f"Desired fields: "
                f"{', '.join(topic.get('desired_fields', []))}\n"
                f"Goal: "
                f"{topic.get('selection_goal')}"
            )
        )

        lines.append("")

    return "\n".join(
        lines
    )


# =========================================================
# CREATE SEARCH PROMPT
# =========================================================

def create_prompt(
    target_database,
    existing_display,
):

    field_gaps = format_field_gaps(
        target_database
    )

    pair_gaps = format_pair_gaps(
        target_database
    )

    search_topics = format_search_topics(
        target_database
    )

    existing_papers = (
        format_existing_papers(
            existing_display
        )
    )

    prompt = f"""
We are performing a SECOND, quantitative-gap-driven
literature search for an IEEE review paper.

The first literature round has already produced a verified
evidence database and comparison table.

Your task now is to find NEW publications that are likely
to fill the specific quantitative gaps below.

============================================================
CURRENT QUANTITATIVE FIELD GAPS
============================================================

{field_gaps}

============================================================
CURRENT PAIRED-FIELD GAPS
============================================================

{pair_gaps}

============================================================
TARGETED SEARCH TOPICS
============================================================

{search_topics}

============================================================
PUBLICATIONS ALREADY IN OUR DATABASE
============================================================

Do NOT intentionally return these papers again:

{existing_papers}

============================================================
PRIMARY SELECTION GOAL
============================================================

Find approximately 10-14 strong NEW candidate
publications.

The final download stage will probably select only 5-8.

Prefer papers that appear capable of providing MULTIPLE
missing quantitative fields in the SAME experimental
system.

Especially valuable candidates include combinations such
as:

1.
efficiency_percent
+
power_density_kw_per_l

2.
semiconductor_voltage_rating_v
+
switching_frequency_khz
+
efficiency_percent

3.
cell_voltage_v
+
semiconductor_voltage_rating_v

4.
rated_power_kw
+
dc_link_voltage_v
+
switching_frequency_khz
+
efficiency_percent

============================================================
POWER DENSITY
============================================================

The current database contains essentially no usable power
density records.

Therefore search aggressively, but scientifically, for
experimentally demonstrated:

- integrated motor drives,
- integrated modular motor drives,
- GaN motor drives,
- SiC motor drives,
- high-power-density traction inverters,
- modular motor drives,
- aerospace electric propulsion inverters,

where power density appears likely to be reported as a
system-level quantitative result.

============================================================
DIRECT SPB
============================================================

Continue searching for direct stacked polyphase bridge
publications, particularly prototypes and experimental
papers reporting:

- semiconductor voltage rating,
- switching frequency,
- efficiency,
- rated power,
- DC-link voltage.

But do not return previously identified SPB publications
simply to increase candidate count.

============================================================
SCIENTIFIC RESTRICTIONS
============================================================

This is candidate discovery only.

Do NOT present unverified quantitative values as evidence.

Do NOT state that a paper experimentally achieved a
specific efficiency or power density unless the available
public information explicitly supports that statement.

Even when such information appears in an abstract or public
page, the candidate must remain:

CANDIDATE_METADATA_ONLY

The actual PDF will be downloaded and processed by a
separate full-text Evidence Extractor later.

============================================================
METADATA
============================================================

Verify DOI, title, authors, year, and venue using Crossref
where possible.

Exclude candidates with obviously unreliable or
unrecoverable bibliographic metadata.

============================================================
OUTPUT
============================================================

Return only the structured QuantitativeLiteratureResult.

Aim for approximately 10-14 strong candidates, but return
fewer if necessary rather than adding poor-quality papers.
"""

    return prompt


# =========================================================
# WRITE MARKDOWN
# =========================================================

def write_markdown(
    search_summary,
    candidates,
    unresolved_targets,
    removed_duplicates,
):

    lines = []

    lines.append(
        "# Quantitative Literature Candidate Papers"
    )

    lines.append("")

    lines.append(
        "These publications were identified during the "
        "second, quantitative-gap-driven literature "
        "search."
    )

    lines.append("")

    lines.append(
        "**Important:** All candidates remain "
        "`CANDIDATE_METADATA_ONLY`. No numerical values "
        "from these publications may enter the review "
        "paper or comparison database until the actual "
        "PDF is processed by the full-text Evidence "
        "Extractor."
    )

    lines.append("")

    lines.append(
        "## Search Summary"
    )

    lines.append("")

    lines.append(
        search_summary
    )

    lines.append("")

    lines.append(
        "## Candidate Papers"
    )

    lines.append("")

    for index, candidate in enumerate(
        candidates,
        start=1,
    ):

        lines.append(
            f"### {index}. "
            f"{candidate.get('title')}"
        )

        lines.append("")

        authors = candidate.get(
            "authors",
            []
        )

        if authors:

            lines.append(
                "- Authors: "
                + ", ".join(
                    authors
                )
            )

        lines.append(
            f"- Year: "
            f"{candidate.get('year')}"
        )

        lines.append(
            f"- Venue: "
            f"{candidate.get('journal_or_venue')}"
        )

        lines.append(
            f"- DOI: "
            f"{candidate.get('doi')}"
        )

        lines.append(
            f"- URL: "
            f"{candidate.get('url')}"
        )

        lines.append(
            f"- Publication type: "
            f"{candidate.get('publication_type')}"
        )

        lines.append(
            f"- Experimental relevance: "
            f"{candidate.get('experimental_relevance')}"
        )

        lines.append(
            f"- Quantitative relevance: "
            f"{candidate.get('quantitative_relevance')}"
        )

        lines.append(
            f"- Full-text access likelihood: "
            f"{candidate.get('full_text_access_likelihood')}"
        )

        topic_ids = (
            candidate.get(
                "matched_topic_ids",
                []
            )
        )

        if topic_ids:

            lines.append(
                "- Search topics: "
                + ", ".join(
                    topic_ids
                )
            )

        fields = (
            candidate.get(
                "expected_quantitative_fields",
                []
            )
        )

        lines.append(
            "- Expected useful fields:"
        )

        if fields:

            for field in fields:

                lines.append(
                    f"  - `{field}`"
                )

        else:

            lines.append(
                "  - None identified"
            )

        pairs = (
            candidate.get(
                "expected_quantitative_pairs",
                []
            )
        )

        lines.append(
            "- Expected useful pairs:"
        )

        if pairs:

            for pair in pairs:

                lines.append(
                    f"  - {pair}"
                )

        else:

            lines.append(
                "  - None identified"
            )

        lines.append(
            "- Selection rationale: "
            + candidate.get(
                "selection_rationale",
                ""
            )
        )

        lines.append("")

    # -----------------------------------------------------
    # REMOVED DUPLICATES
    # -----------------------------------------------------

    lines.append(
        "## Automatically Removed Duplicates"
    )

    lines.append("")

    if removed_duplicates:

        for item in removed_duplicates:

            lines.append(
                (
                    f"- {item.get('title')} — "
                    f"{item.get('reason')}"
                )
            )

    else:

        lines.append(
            "- None"
        )

    lines.append("")

    # -----------------------------------------------------
    # UNRESOLVED TARGETS
    # -----------------------------------------------------

    lines.append(
        "## Unresolved Quantitative Targets"
    )

    lines.append("")

    if unresolved_targets:

        for target in unresolved_targets:

            lines.append(
                f"- {target}"
            )

    else:

        lines.append(
            "- None reported by the search agent."
        )

    lines.append("")

    OUTPUT_MD.write_text(
        "\n".join(
            lines
        ),
        encoding="utf-8",
    )


# =========================================================
# MAIN
# =========================================================

async def main():

    print()
    print(
        "========================================"
    )

    print(
        "QUANTITATIVE LITERATURE SEARCH"
    )

    print(
        "========================================"
    )

    print()

    # -----------------------------------------------------
    # TARGETS
    # -----------------------------------------------------

    if not TARGET_FILE.exists():

        print(
            "ERROR:"
        )

        print(
            "Could not find:"
        )

        print(
            TARGET_FILE
        )

        print()

        print(
            "Run first:"
        )

        print()

        print(
            "python "
            "build_quantitative_literature_targets.py"
        )

        return

    target_database = load_json(
        TARGET_FILE,
        {},
    )

    # -----------------------------------------------------
    # EXISTING PAPERS
    # -----------------------------------------------------

    (
        existing_dois,
        existing_titles,
        existing_display,
    ) = build_existing_identifiers()

    print(
        f"Existing literature records: "
        f"{len(existing_display)}"
    )

    print()

    # -----------------------------------------------------
    # PROMPT
    # -----------------------------------------------------

    prompt = create_prompt(
        target_database,
        existing_display,
    )

    # -----------------------------------------------------
    # RUN AGENT
    # -----------------------------------------------------

    print(
        "Running quantitative literature agent..."
    )

    print()

    print(
        "This step uses API credits and web search."
    )

    print()

    result = await Runner.run(
        quantitative_literature_agent,
        prompt,
        max_turns=40,
    )

    output = (
        result.final_output
        .model_dump()
    )

    raw_candidates = (
        output.get(
            "candidates",
            []
        )
    )

    # -----------------------------------------------------
    # DETERMINISTIC DUPLICATE FILTER
    # -----------------------------------------------------

    (
        candidates,
        removed_duplicates,
    ) = remove_duplicates(
        raw_candidates,
        existing_dois,
        existing_titles,
    )

    # -----------------------------------------------------
    # FINAL DATABASE
    # -----------------------------------------------------

    final_database = {
        "search_summary":
            output.get(
                "search_summary",
                ""
            ),

        "candidate_count_before_deduplication":
            len(
                raw_candidates
            ),

        "candidate_count_after_deduplication":
            len(
                candidates
            ),

        "candidates":
            candidates,

        "removed_duplicates":
            removed_duplicates,

        "unresolved_targets":
            output.get(
                "unresolved_targets",
                []
            ),

        "verification_policy":
            (
                "All candidates are metadata/discovery "
                "records only. Scientific and numerical "
                "claims require later full-text evidence "
                "extraction."
            ),
    }

    # -----------------------------------------------------
    # SAVE JSON
    # -----------------------------------------------------

    OUTPUT_JSON.write_text(
        json.dumps(
            final_database,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # MARKDOWN
    # -----------------------------------------------------

    write_markdown(
        final_database[
            "search_summary"
        ],
        candidates,
        final_database[
            "unresolved_targets"
        ],
        removed_duplicates,
    )

    # -----------------------------------------------------
    # TERMINAL SUMMARY
    # -----------------------------------------------------

    print(
        "========================================"
    )

    print(
        "SEARCH COMPLETE"
    )

    print(
        "========================================"
    )

    print()

    print(
        f"Candidates returned by agent: "
        f"{len(raw_candidates)}"
    )

    print(
        f"Duplicates removed:          "
        f"{len(removed_duplicates)}"
    )

    print(
        f"New candidate papers:        "
        f"{len(candidates)}"
    )

    print()

    print(
        "Candidate list:"
    )

    print(
        "----------------------------------------"
    )

    for index, candidate in enumerate(
        candidates,
        start=1,
    ):

        fields = candidate.get(
            "expected_quantitative_fields",
            []
        )

        print(
            f"{index:2d}. "
            f"{candidate.get('title')}"
        )

        print(
            f"    DOI: "
            f"{candidate.get('doi')}"
        )

        print(
            f"    Fields: "
            f"{', '.join(fields)}"
        )

        print()

    print(
        "Files created:"
    )

    print(
        OUTPUT_JSON
    )

    print(
        OUTPUT_MD
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "Do NOT download everything yet."
    )

    print(
        "The next step will deterministically rank "
        "these candidates according to the actual "
        "quantitative gaps."
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )