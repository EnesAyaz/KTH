import asyncio
from pathlib import Path

from dotenv import load_dotenv
from agents import Runner

from paper_agents.editor import editor_agent


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

REVIEW_FILE = (
    ROOT_DIR
    / "output"
    / "review_report.md"
)

EVIDENCE_FILE = (
    ROOT_DIR
    / "data"
    / "evidence.json"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "output"
    / "sections"
    / "converter_architecture_revised.tex"
)


# =========================================================
# MAIN
# =========================================================

async def main():

    manuscript = SECTION_FILE.read_text(
        encoding="utf-8"
    )

    review = REVIEW_FILE.read_text(
        encoding="utf-8"
    )

    evidence = EVIDENCE_FILE.read_text(
        encoding="utf-8"
    )

    prompt = f"""
Revise the manuscript according to the peer-review report.

============================================================
ORIGINAL MANUSCRIPT
============================================================

{manuscript}

============================================================
PEER-REVIEW REPORT
============================================================

{review}

============================================================
VERIFIED SCIENTIFIC EVIDENCE
============================================================

{evidence}

============================================================
REVISION REQUIREMENT
============================================================

Address all valid CRITICAL and MAJOR reviewer comments.

Address MINOR comments when doing so improves clarity.

Do not introduce unsupported information.

If a requested change requires evidence that is not
available, insert:

% ADDITIONAL LITERATURE REQUIRED

Return the complete revised LaTeX section.
"""

    print()
    print("==============================")
    print("EDITOR AGENT")
    print("==============================")
    print()

    result = await Runner.run(
        editor_agent,
        prompt,
    )

    revised = str(
        result.final_output
    )

    OUTPUT_FILE.write_text(
        revised,
        encoding="utf-8",
    )

    print(revised)

    print()
    print("==============================")
    print("REVISED SECTION SAVED")
    print("==============================")
    print()
    print(OUTPUT_FILE)
    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    asyncio.run(main())