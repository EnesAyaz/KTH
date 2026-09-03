import asyncio
from pathlib import Path

from dotenv import load_dotenv
from agents import Runner

from paper_agents.reviewer import reviewer_agent


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

SECTION_FILE = (
    ROOT_DIR
    / "output"
    / "sections"
    / "converter_architecture.tex"
)

EVIDENCE_FILE = (
    ROOT_DIR
    / "data"
    / "evidence.json"
)

REVIEW_FILE = (
    ROOT_DIR
    / "output"
    / "review_report.md"
)


# =========================================================
# MAIN
# =========================================================

async def main():

    manuscript = SECTION_FILE.read_text(
        encoding="utf-8"
    )

    evidence = EVIDENCE_FILE.read_text(
        encoding="utf-8"
    )

    prompt = f"""
Review the manuscript section below.

============================================================
MANUSCRIPT
============================================================

{manuscript}

============================================================
VERIFIED SCIENTIFIC EVIDENCE
============================================================

{evidence}

============================================================
SPECIAL REVIEW TASK
============================================================

Pay particular attention to:

- unsupported technical statements,
- citation validity,
- incorrect interpretation,
- missing operating conditions,
- overstated benefits,
- insufficient discussion of disadvantages,
- weak comparisons,
- lack of experimental evidence,
- statements that go beyond the supplied evidence.
"""

    print()
    print("==============================")
    print("REVIEWER AGENT")
    print("==============================")
    print()

    result = await Runner.run(
        reviewer_agent,
        prompt,
    )

    review = str(
        result.final_output
    )

    print(review)

    REVIEW_FILE.write_text(
        review,
        encoding="utf-8",
    )

    print()
    print("==============================")
    print("REVIEW SAVED")
    print("==============================")
    print()
    print(REVIEW_FILE)
    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    asyncio.run(main())