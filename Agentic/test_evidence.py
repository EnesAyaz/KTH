import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
from agents import Runner

from paper_agents.evidence_extractor import evidence_agent


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# PROJECT PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

DATA_DIR = ROOT_DIR / "data"

EVIDENCE_FILE = DATA_DIR / "evidence.json"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# MAIN
# =========================================================

async def main():

    print()
    print("========================================")
    print("STARTING SCIENTIFIC EVIDENCE EXTRACTION")
    print("========================================")
    print()

    prompt = """
First list the PDF files available in the local papers folder.

Analyze the paper corresponding to the citation key:

Jin2017

If the filename is not exactly Jin2017.pdf, identify the
correct PDF by its title.

Extract approximately 5-10 high-value scientific claims
relevant to a review of stacked polyphase bridge converters.

Focus particularly on:

- converter architecture,
- operating principle,
- modulation,
- power losses,
- semiconductor stress,
- voltage scaling,
- number of phases,
- number of converter cells,
- experimental setup,
- quantitative results,
- advantages,
- limitations.

You MUST inspect the PDF using the available PDF tools.

Do not rely only on bibliographic metadata.

For every claim:

- assign a claim_id,
- provide citation_key,
- provide page number when possible,
- classify evidence_type,
- assign relevant_sections,
- record numerical values,
- assign verification_level,
- assign confidence.

Do not invent missing information.
"""

    result = await Runner.run(
        evidence_agent,
        prompt,
    )

    evidence = result.final_output

    evidence_dict = evidence.model_dump()

    # -----------------------------------------------------
    # PRINT RESULT
    # -----------------------------------------------------

    print()
    print("==============================")
    print("EXTRACTED EVIDENCE")
    print("==============================")
    print()

    print(
        json.dumps(
            evidence_dict,
            indent=2,
            ensure_ascii=False,
        )
    )

    # -----------------------------------------------------
    # SAVE RESULT
    # -----------------------------------------------------

    EVIDENCE_FILE.write_text(
        json.dumps(
            evidence_dict,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("==============================")
    print("EVIDENCE SAVED")
    print("==============================")
    print()
    print(EVIDENCE_FILE)
    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    asyncio.run(main())