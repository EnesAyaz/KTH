import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
from agents import Runner

from paper_agents.writer import writer_agent
from paper_agents.reviewer import reviewer_agent
from paper_agents.editor import editor_agent

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

SECTIONS_DIR = (
    OUTPUT_DIR
    / "sections"
)

DRAFT_FILE = (
    SECTIONS_DIR
    / "converter_architecture.tex"
)

REVIEW_FILE = (
    OUTPUT_DIR
    / "review_report.md"
)

REVISED_FILE = (
    SECTIONS_DIR
    / "converter_architecture_revised.tex"
)

SECTIONS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# LOAD VERIFIED EVIDENCE
# =========================================================

def load_verified_evidence():

    data = json.loads(
        EVIDENCE_FILE.read_text(
            encoding="utf-8"
        )
    )

    database = {
        "papers": []
    }

    for paper in data.get(
        "papers",
        []
    ):

        claims = []

        for claim in paper.get(
            "claims",
            []
        ):

            if (
                claim.get(
                    "verification_level"
                )
                == "FULL_TEXT_VERIFIED"
            ):

                claims.append(
                    claim
                )

        if claims:

            database[
                "papers"
            ].append(
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
                        claims,
                }
            )

    return database


# =========================================================
# WRITER
# =========================================================

async def write_section(
    evidence_text: str
):

    print()
    print("==============================")
    print("1. WRITER")
    print("==============================")
    print()

    prompt = f"""
Write:

\\section{{Stacked Polyphase Bridge Architecture}}

Use ONLY the evidence supplied below.

============================================================
VERIFIED EVIDENCE
============================================================

{evidence_text}

============================================================

Target approximately 700-1000 words.

Explain:

- architecture,
- operating principle,
- relationship between converter cells and machine winding
  groups,
- DC-side stacking,
- voltage scaling,
- benefits,
- limitations,
- experimental evidence,
- unresolved questions.

Return LaTeX only.
"""

    result = await Runner.run(
        writer_agent,
        prompt,
    )

    draft = str(
        result.final_output
    )

    DRAFT_FILE.write_text(
        draft,
        encoding="utf-8",
    )

    return draft


# =========================================================
# REVIEWER
# =========================================================

async def review_section(
    draft: str,
    evidence_text: str,
):

    print()
    print("==============================")
    print("2. REVIEWER")
    print("==============================")
    print()

    prompt = f"""
Review this manuscript section.

============================================================
MANUSCRIPT
============================================================

{draft}

============================================================
VERIFIED EVIDENCE
============================================================

{evidence_text}

============================================================

Identify unsupported statements, citation problems,
overstatements, missing limitations, weak comparisons,
and missing evidence.
"""

    result = await Runner.run(
        reviewer_agent,
        prompt,
    )

    review = str(
        result.final_output
    )

    REVIEW_FILE.write_text(
        review,
        encoding="utf-8",
    )

    return review


# =========================================================
# EDITOR
# =========================================================

async def edit_section(
    draft: str,
    review: str,
    evidence_text: str,
):

    print()
    print("==============================")
    print("3. EDITOR")
    print("==============================")
    print()

    prompt = f"""
Revise the manuscript.

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

Fix valid reviewer criticisms.

Do not introduce unsupported information.

Return complete revised LaTeX only.
"""

    result = await Runner.run(
        editor_agent,
        prompt,
    )

    revised = str(
        result.final_output
    )

    REVISED_FILE.write_text(
        revised,
        encoding="utf-8",
    )

    return revised


# =========================================================
# MAIN
# =========================================================

async def main():

    print()
    print("==========================================")
    print("AGENTIC REVIEW-PAPER SECTION PIPELINE")
    print("==========================================")
    print()

    # -----------------------------------------------------
    # LOAD EVIDENCE
    # -----------------------------------------------------

    evidence = load_verified_evidence()

    claim_count = sum(
        len(paper["claims"])
        for paper in evidence["papers"]
    )

    print(
        f"FULL_TEXT_VERIFIED claims: "
        f"{claim_count}"
    )

    if claim_count == 0:

        print()
        print(
            "No verified evidence available."
        )

        print(
            "Run test_evidence.py first."
        )

        return

    evidence_text = json.dumps(
        evidence,
        indent=2,
        ensure_ascii=False,
    )

    # -----------------------------------------------------
    # WRITER
    # -----------------------------------------------------

    draft = await write_section(
        evidence_text
    )

    # -----------------------------------------------------
    # CHECK DRAFT CITATIONS
    # -----------------------------------------------------

    print()
    print("==============================")
    print("DRAFT CITATION CHECK")
    print("==============================")
    print()

    draft_check = check_citations(
        DRAFT_FILE,
        EVIDENCE_FILE,
    )

    if draft_check["invalid"]:

        print(
            "INVALID CITATIONS FOUND:"
        )

        for key in sorted(
            draft_check["invalid"]
        ):

            print(
                f"  {key}"
            )

        print()
        print(
            "Pipeline stopped."
        )

        return

    print(
        "Draft citation check PASSED."
    )

    # -----------------------------------------------------
    # REVIEWER
    # -----------------------------------------------------

    review = await review_section(
        draft,
        evidence_text,
    )

    # -----------------------------------------------------
    # EDITOR
    # -----------------------------------------------------

    revised = await edit_section(
        draft,
        review,
        evidence_text,
    )

    # -----------------------------------------------------
    # CHECK REVISED CITATIONS
    # -----------------------------------------------------

    print()
    print("==============================")
    print("FINAL CITATION CHECK")
    print("==============================")
    print()

    final_check = check_citations(
        REVISED_FILE,
        EVIDENCE_FILE,
    )

    if final_check["invalid"]:

        print(
            "INVALID CITATIONS FOUND:"
        )

        for key in sorted(
            final_check["invalid"]
        ):

            print(
                f"  {key}"
            )

        print()
        print(
            "Revised manuscript rejected."
        )

        return

    print(
        "Final citation check PASSED."
    )

    # -----------------------------------------------------
    # COMPLETE
    # -----------------------------------------------------

    print()
    print("==========================================")
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("==========================================")
    print()

    print(
        "Draft:"
    )
    print(
        DRAFT_FILE
    )

    print()
    print(
        "Review:"
    )
    print(
        REVIEW_FILE
    )

    print()
    print(
        "Revised:"
    )
    print(
        REVISED_FILE
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    asyncio.run(main())