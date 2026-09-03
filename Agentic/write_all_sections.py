import argparse
import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
from agents import Runner

from paper_agents.writer import (
    writer_agent,
)

from paper_agents.reviewer import (
    reviewer_agent,
)

from paper_agents.editor import (
    editor_agent,
)

from paper_config import SECTIONS

from tools.evidence_selector import (
    select_evidence_for_section,
    count_claims,
    count_sources,
)

from tools.citation_checker import (
    check_citations,
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

EVIDENCE_FILE = (
    ROOT_DIR
    / "data"
    / "evidence.json"
)

OUTPUT_DIR = (
    ROOT_DIR
    / "output"
)

DRAFTS_DIR = (
    OUTPUT_DIR
    / "drafts"
)

SECTIONS_DIR = (
    OUTPUT_DIR
    / "sections"
)

REVIEWS_DIR = (
    OUTPUT_DIR
    / "reviews"
)


for directory in [
    DRAFTS_DIR,
    SECTIONS_DIR,
    REVIEWS_DIR,
]:

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )


# =========================================================
# WRITER
# =========================================================

async def write_section(
    section,
    evidence,
):

    title = section["title"]

    target_words = section[
        "target_words"
    ]

    objectives = section[
        "objectives"
    ]

    evidence_text = json.dumps(
        evidence,
        indent=2,
        ensure_ascii=False,
    )

    objective_text = "\n".join(
        f"- {item}"
        for item in objectives
    )

    prompt = f"""
Write the following review-paper section:

\\section{{{title}}}

Target length:

Approximately {target_words} words.

============================================================
SECTION OBJECTIVES
============================================================

{objective_text}

============================================================
FULL-TEXT VERIFIED EVIDENCE
============================================================

{evidence_text}

============================================================
RULES
============================================================

Use ONLY the supplied evidence for technical claims.

Synthesize the literature instead of describing one paper
after another.

Compare agreements, disagreements, advantages, limitations,
and experimental evidence.

Do not invent citations.

Do not invent numerical values.

If evidence is insufficient for a statement, write:

% REFERENCE REQUIRED

If substantially more literature is needed, write:

% ADDITIONAL LITERATURE REQUIRED

Return LaTeX only.
"""

    result = await Runner.run(
        writer_agent,
        prompt,
    )

    return str(
        result.final_output
    )


# =========================================================
# REVIEWER
# =========================================================

async def review_section(
    section,
    draft,
    evidence,
):

    evidence_text = json.dumps(
        evidence,
        indent=2,
        ensure_ascii=False,
    )

    prompt = f"""
Critically review this review-paper section.

Section:

{section["title"]}

============================================================
MANUSCRIPT
============================================================

{draft}

============================================================
VERIFIED EVIDENCE
============================================================

{evidence_text}

============================================================

Identify:

- unsupported claims,
- citation problems,
- overstatements,
- missing limitations,
- weak synthesis,
- unjustified numerical comparisons,
- missing operating conditions,
- statements that go beyond the evidence.
"""

    result = await Runner.run(
        reviewer_agent,
        prompt,
    )

    return str(
        result.final_output
    )


# =========================================================
# EDITOR
# =========================================================

async def edit_section(
    section,
    draft,
    review,
    evidence,
):

    evidence_text = json.dumps(
        evidence,
        indent=2,
        ensure_ascii=False,
    )

    prompt = f"""
Revise this section according to the reviewer report.

Section:

{section["title"]}

============================================================
ORIGINAL MANUSCRIPT
============================================================

{draft}

============================================================
REVIEW REPORT
============================================================

{review}

============================================================
VERIFIED EVIDENCE
============================================================

{evidence_text}

============================================================

Fix valid CRITICAL and MAJOR problems.

Do not invent new citations or numerical information.

When available evidence cannot satisfy the requested
revision, retain:

% ADDITIONAL LITERATURE REQUIRED

Return the complete revised LaTeX section.
"""

    result = await Runner.run(
        editor_agent,
        prompt,
    )

    return str(
        result.final_output
    )


# =========================================================
# PROCESS SECTION
# =========================================================

async def process_section(
    section,
    force=False,
):

    number = section["number"]

    title = section["title"]

    filename = section[
        "filename"
    ]

    evidence_section = section[
        "evidence_section"
    ]

    final_file = (
        SECTIONS_DIR
        / filename
    )

    draft_file = (
        DRAFTS_DIR
        / filename
    )

    review_filename = (
        Path(filename).stem
        + "_review.md"
    )

    review_file = (
        REVIEWS_DIR
        / review_filename
    )

    print()
    print(
        "========================================"
    )

    print(
        f"SECTION {number}: {title}"
    )

    print(
        "========================================"
    )

    # -----------------------------------------------------
    # SKIP COMPLETED
    # -----------------------------------------------------

    if (
        final_file.exists()
        and not force
    ):

        print(
            "Final section already exists."
        )

        print(
            "Skipping."
        )

        return

    # -----------------------------------------------------
    # EVIDENCE
    # -----------------------------------------------------

    evidence = (
        select_evidence_for_section(
            EVIDENCE_FILE,
            evidence_section,
            full_text_only=True,
        )
    )

    claim_count = count_claims(
        evidence
    )

    source_count = count_sources(
        evidence
    )

    print(
        f"Sources: {source_count}"
    )

    print(
        f"Claims: {claim_count}"
    )

    # -----------------------------------------------------
    # NO EVIDENCE
    # -----------------------------------------------------

    if claim_count == 0:

        placeholder = (
            f"\\section{{{title}}}\n\n"
            "% ADDITIONAL LITERATURE REQUIRED\n"
        )

        final_file.write_text(
            placeholder,
            encoding="utf-8",
        )

        print(
            "No verified evidence."
        )

        print(
            "Placeholder section created."
        )

        return

    # -----------------------------------------------------
    # WRITER
    # -----------------------------------------------------

    print()
    print(
        "Running Writer Agent..."
    )

    draft = await write_section(
        section,
        evidence,
    )

    draft_file.write_text(
        draft,
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # DRAFT CITATION CHECK
    # -----------------------------------------------------

    draft_check = (
        check_citations(
            draft_file,
            EVIDENCE_FILE,
        )
    )

    if draft_check["invalid"]:

        print()
        print(
            "DRAFT REJECTED."
        )

        print(
            "Invalid citation keys:"
        )

        for key in sorted(
            draft_check["invalid"]
        ):

            print(
                f"  {key}"
            )

        return

    print(
        "Draft citation check passed."
    )

    # -----------------------------------------------------
    # REVIEWER
    # -----------------------------------------------------

    print(
        "Running Reviewer Agent..."
    )

    review = await review_section(
        section,
        draft,
        evidence,
    )

    review_file.write_text(
        review,
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # EDITOR
    # -----------------------------------------------------

    print(
        "Running Editor Agent..."
    )

    revised = await edit_section(
        section,
        draft,
        review,
        evidence,
    )

    final_file.write_text(
        revised,
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # FINAL CITATION CHECK
    # -----------------------------------------------------

    final_check = (
        check_citations(
            final_file,
            EVIDENCE_FILE,
        )
    )

    if final_check["invalid"]:

        print()
        print(
            "FINAL SECTION REJECTED."
        )

        print(
            "Invalid citation keys:"
        )

        for key in sorted(
            final_check["invalid"]
        ):

            print(
                f"  {key}"
            )

        # Rename invalid output instead of silently
        # accepting it.

        rejected_file = (
            final_file.with_suffix(
                ".rejected.tex"
            )
        )

        final_file.rename(
            rejected_file
        )

        return

    print(
        "Final citation check passed."
    )

    print(
        f"Saved:\n{final_file}"
    )


# =========================================================
# MAIN
# =========================================================

async def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--section",
        type=int,
        default=None,
        help=(
            "Process one section number only."
        ),
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Overwrite existing final sections."
        ),
    )

    args = parser.parse_args()

    if not EVIDENCE_FILE.exists():

        print(
            "evidence.json does not exist."
        )

        return

    print()
    print(
        "========================================"
    )

    print(
        "AUTOMATIC PAPER WRITING PIPELINE"
    )

    print(
        "========================================"
    )

    # -----------------------------------------------------
    # PROCESS
    # -----------------------------------------------------

    for section in SECTIONS:

        if (
            args.section is not None
            and section["number"]
            != args.section
        ):

            continue

        try:

            await process_section(
                section,
                force=args.force,
            )

        except Exception as error:

            print()
            print(
                "ERROR:"
            )

            print(error)

            print()
            print(
                "Moving to next section."
            )

    print()
    print(
        "========================================"
    )

    print(
        "WRITING PIPELINE FINISHED"
    )

    print(
        "========================================"
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )