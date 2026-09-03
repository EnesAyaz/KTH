import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
from agents import Runner

from paper_agents.writer import writer_agent


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
    / "sections"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "converter_architecture.tex"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# LOAD FULL-TEXT VERIFIED EVIDENCE
# =========================================================

def load_verified_evidence():

    data = json.loads(
        EVIDENCE_FILE.read_text(
            encoding="utf-8"
        )
    )

    verified_database = {
        "papers": []
    }

    for paper in data.get("papers", []):

        verified_claims = []

        for claim in paper.get("claims", []):

            if (
                claim.get("verification_level")
                == "FULL_TEXT_VERIFIED"
            ):
                verified_claims.append(claim)

        if verified_claims:

            verified_database["papers"].append(
                {
                    "citation_key":
                        paper.get("citation_key"),

                    "title":
                        paper.get("title"),

                    "pdf_filename":
                        paper.get("pdf_filename"),

                    "claims":
                        verified_claims,
                }
            )

    return verified_database


# =========================================================
# MAIN
# =========================================================

async def main():

    evidence = load_verified_evidence()

    number_of_claims = sum(
        len(paper["claims"])
        for paper in evidence["papers"]
    )

    print()
    print("==============================")
    print("WRITER AGENT")
    print("==============================")
    print()
    print(
        f"FULL_TEXT_VERIFIED claims available: "
        f"{number_of_claims}"
    )
    print()

    if number_of_claims == 0:

        print(
            "No FULL_TEXT_VERIFIED evidence found."
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

    section_name = (
        "Stacked Polyphase Bridge Architecture"
    )

    prompt = f"""
Write the following review-paper section:

\\section{{{section_name}}}

Use ONLY the verified evidence supplied below.

============================================================
VERIFIED SCIENTIFIC EVIDENCE
============================================================

{evidence_text}

============================================================
SECTION OBJECTIVES
============================================================

Write approximately 700-1000 words.

The section should:

1. Define the stacked polyphase bridge architecture.

2. Explain its operating principle.

3. Explain the relationship between converter cells and
   electrically separated machine winding groups.

4. Explain the significance of DC-side stacking.

5. Discuss voltage-scaling implications.

6. Discuss relevant modulation considerations.

7. Discuss benefits supported by evidence.

8. Discuss limitations supported by evidence.

9. Clearly distinguish experimentally demonstrated results
   from theoretical or proposed benefits.

10. Identify areas where current evidence is insufficient.

Only cite citation keys contained in the evidence above.

If evidence does not support an important statement, use:

% REFERENCE REQUIRED

Return LaTeX only.
"""

    result = await Runner.run(
        writer_agent,
        prompt,
    )

    section = str(
        result.final_output
    )

    OUTPUT_FILE.write_text(
        section,
        encoding="utf-8",
    )

    print(section)

    print()
    print("==============================")
    print("SECTION SAVED")
    print("==============================")
    print()
    print(OUTPUT_FILE)
    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    asyncio.run(main())