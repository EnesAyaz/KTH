import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
from agents import Runner

from paper_agents.targeted_literature import (
    targeted_literature_agent,
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


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

TARGETS_FILE = (
    DATA_DIR
    / "literature_targets.json"
)

EXISTING_PAPERS_FILE = (
    DATA_DIR
    / "papers.json"
)

CANDIDATES_FILE = (
    DATA_DIR
    / "candidate_papers.json"
)

DOWNLOAD_REPORT_FILE = (
    OUTPUT_DIR
    / "papers_to_download.md"
)


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# LOAD JSON
# =========================================================

def load_json(
    path,
    default=None,
):

    if default is None:
        default = {}

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
# CREATE MARKDOWN REPORT
# =========================================================

def create_download_report(
    result_data,
):

    lines = []

    lines.append(
        "# Candidate Papers to Download"
    )

    lines.append("")

    lines.append(
        "These publications were identified through "
        "targeted literature discovery."
    )

    lines.append("")

    lines.append(
        "**Important:** They are not yet full-text verified."
    )

    lines.append(
        "Download and place selected PDFs in the `papers/` "
        "folder before scientific claims are used."
    )

    lines.append("")

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    lines.append(
        "## Search Summary"
    )

    lines.append("")

    lines.append(
        result_data.get(
            "search_summary",
            ""
        )
    )

    lines.append("")

    candidates = result_data.get(
        "candidates",
        []
    )

    # -----------------------------------------------------
    # CANDIDATES
    # -----------------------------------------------------

    lines.append(
        f"## Candidates ({len(candidates)})"
    )

    lines.append("")

    for index, paper in enumerate(
        candidates,
        start=1,
    ):

        title = paper.get(
            "title",
            "Unknown title",
        )

        lines.append(
            f"### {index}. {title}"
        )

        lines.append("")

        authors = paper.get(
            "authors",
            []
        )

        if authors:

            lines.append(
                "**Authors:** "
                + ", ".join(
                    authors
                )
            )

            lines.append("")

        year = paper.get(
            "year"
        )

        if year is not None:

            lines.append(
                f"**Year:** {year}"
            )

            lines.append("")

        venue = paper.get(
            "journal_or_venue"
        )

        if venue:

            lines.append(
                f"**Venue:** {venue}"
            )

            lines.append("")

        doi = paper.get(
            "doi"
        )

        if doi:

            lines.append(
                f"**DOI:** `{doi}`"
            )

            lines.append("")

        url = paper.get(
            "url"
        )

        if url:

            lines.append(
                f"**URL:** {url}"
            )

            lines.append("")

        publication_type = paper.get(
            "publication_type"
        )

        if publication_type:

            lines.append(
                f"**Type:** {publication_type}"
            )

            lines.append("")

        topics = paper.get(
            "target_topics",
            []
        )

        if topics:

            lines.append(
                "**Target topics:**"
            )

            lines.append("")

            for topic in topics:

                lines.append(
                    f"- {topic}"
                )

            lines.append("")

        fields = paper.get(
            "expected_useful_fields",
            []
        )

        if fields:

            lines.append(
                "**Potential comparison fields:**"
            )

            lines.append("")

            for field in fields:

                lines.append(
                    f"- `{field}`"
                )

            lines.append("")

        reason = paper.get(
            "reason_for_selection"
        )

        if reason:

            lines.append(
                "**Why this paper may be useful:**"
            )

            lines.append("")

            lines.append(
                reason
            )

            lines.append("")

        experimental = paper.get(
            "experimental_relevance"
        )

        if experimental:

            lines.append(
                "**Experimental relevance:**"
            )

            lines.append("")

            lines.append(
                experimental
            )

            lines.append("")

        full_text_value = paper.get(
            "likely_full_text_value"
        )

        if full_text_value:

            lines.append(
                "**Expected full-text value:**"
            )

            lines.append("")

            lines.append(
                full_text_value
            )

            lines.append("")

        lines.append(
            "**Current verification:** "
            "`CANDIDATE_METADATA_ONLY`"
        )

        lines.append("")

        lines.append("---")

        lines.append("")

    # -----------------------------------------------------
    # UNRESOLVED TOPICS
    # -----------------------------------------------------

    unresolved = result_data.get(
        "unresolved_topics",
        []
    )

    if unresolved:

        lines.append(
            "## Unresolved Literature Gaps"
        )

        lines.append("")

        for topic in unresolved:

            lines.append(
                f"- {topic}"
            )

        lines.append("")

    DOWNLOAD_REPORT_FILE.write_text(
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
        "TARGETED LITERATURE SEARCH"
    )

    print(
        "========================================"
    )

    print()

    # -----------------------------------------------------
    # CHECK TARGET FILE
    # -----------------------------------------------------

    if not TARGETS_FILE.exists():

        print(
            "literature_targets.json does not exist."
        )

        print()

        print(
            "Run this first:"
        )

        print()

        print(
            "python build_literature_targets.py"
        )

        return

    # -----------------------------------------------------
    # LOAD TARGETS
    # -----------------------------------------------------

    targets = load_json(
        TARGETS_FILE,
        {},
    )

    # -----------------------------------------------------
    # LOAD EXISTING PAPERS
    # -----------------------------------------------------

    existing_papers = load_json(
        EXISTING_PAPERS_FILE,
        {
            "papers": []
        },
    )

    # -----------------------------------------------------
    # CONVERT TO TEXT
    # -----------------------------------------------------

    targets_text = json.dumps(
        targets,
        indent=2,
        ensure_ascii=False,
    )

    existing_text = json.dumps(
        existing_papers,
        indent=2,
        ensure_ascii=False,
    )

    # -----------------------------------------------------
    # PROMPT
    # -----------------------------------------------------

    prompt = f"""
Perform a targeted scientific literature search for the
review paper.

============================================================
CURRENT LITERATURE GAPS
============================================================

{targets_text}

============================================================
PAPERS ALREADY IN THE PROJECT
============================================================

{existing_text}

============================================================
TASK
============================================================

Find approximately 8-15 strong candidate publications that
can help fill the CRITICAL and HIGH-priority gaps.

Do not recommend publications already present in the
project.

Prioritize papers that are likely to provide multiple
quantitative comparison fields simultaneously.

Strongly prioritize experimental converter and motor-drive
papers.

Also include seminal architecture papers when necessary.

Use Web Search and Crossref to verify bibliographic
metadata.

Prefer papers with verified DOI information.

Remember:

These are candidate papers only.

Do NOT treat bibliographic discovery as full-text technical
verification.
"""

    # -----------------------------------------------------
    # RUN AGENT
    # -----------------------------------------------------

    print(
        "Searching literature..."
    )

    print()

    result = await Runner.run(
        targeted_literature_agent,
        prompt,
        max_turns=30,
    )

    output = (
        result.final_output
    )

    data = (
        output.model_dump()
    )

    # -----------------------------------------------------
    # SAVE JSON
    # -----------------------------------------------------

    CANDIDATES_FILE.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # SAVE HUMAN-READABLE REPORT
    # -----------------------------------------------------

    create_download_report(
        data
    )

    # -----------------------------------------------------
    # TERMINAL RESULT
    # -----------------------------------------------------

    candidates = data.get(
        "candidates",
        []
    )

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
        f"Candidate papers found: "
        f"{len(candidates)}"
    )

    print()

    for index, paper in enumerate(
        candidates,
        start=1,
    ):

        print(
            f"{index}. "
            f"{paper.get('title')}"
        )

        doi = paper.get(
            "doi"
        )

        if doi:

            print(
                f"   DOI: {doi}"
            )

        print()

    print(
        "Files created:"
    )

    print()

    print(
        CANDIDATES_FILE
    )

    print(
        DOWNLOAD_REPORT_FILE
    )

    print()

    print(
        "IMPORTANT:"
    )

    print()

    print(
        "Do NOT add these papers to evidence.json yet."
    )

    print(
        "They must first be downloaded and inspected "
        "from full text."
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )