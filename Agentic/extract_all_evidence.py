import argparse
import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
from agents import Runner

from paper_agents.evidence_extractor import evidence_agent


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

DATA_DIR = ROOT_DIR / "data"
PAPERS_DIR = ROOT_DIR / "papers"

PAPERS_DATABASE_FILE = (
    DATA_DIR / "papers.json"
)

EVIDENCE_FILE = (
    DATA_DIR / "evidence.json"
)

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

PAPERS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# LOAD PAPERS DATABASE
# =========================================================

def load_papers_database():

    if not PAPERS_DATABASE_FILE.exists():

        raise FileNotFoundError(
            f"Could not find:\n"
            f"{PAPERS_DATABASE_FILE}"
        )

    data = json.loads(
        PAPERS_DATABASE_FILE.read_text(
            encoding="utf-8"
        )
    )

    # Support both:
    #
    # {
    #     "search_topic": "...",
    #     "papers": [...]
    # }
    #
    # and:
    #
    # [...]

    if isinstance(data, list):
        return data

    return data.get(
        "papers",
        []
    )


# =========================================================
# LOAD EXISTING EVIDENCE
# =========================================================

def load_existing_evidence():

    if not EVIDENCE_FILE.exists():

        return {
            "papers": []
        }

    try:

        data = json.loads(
            EVIDENCE_FILE.read_text(
                encoding="utf-8"
            )
        )

        if not isinstance(data, dict):

            return {
                "papers": []
            }

        if "papers" not in data:

            data["papers"] = []

        return data

    except json.JSONDecodeError:

        return {
            "papers": []
        }


# =========================================================
# SAVE EVIDENCE
# =========================================================

def save_evidence(
    evidence_database
):

    EVIDENCE_FILE.write_text(
        json.dumps(
            evidence_database,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


# =========================================================
# FIND EXISTING PAPER
# =========================================================

def find_existing_paper(
    evidence_database,
    citation_key,
):

    for index, paper in enumerate(
        evidence_database.get(
            "papers",
            []
        )
    ):

        if (
            paper.get("citation_key")
            == citation_key
        ):

            return index

    return None


# =========================================================
# EXTRACT ONE PAPER
# =========================================================

async def extract_one_paper(
    paper,
):

    citation_key = paper.get(
        "citation_key"
    )

    title = paper.get(
        "title",
        ""
    )

    doi = paper.get(
        "doi"
    )

    pdf_filename = (
        f"{citation_key}.pdf"
    )

    pdf_path = (
        PAPERS_DIR
        / pdf_filename
    )

    if not pdf_path.exists():

        print()
        print(
            f"PDF NOT FOUND: "
            f"{pdf_filename}"
        )

        print(
            "Skipping this paper."
        )

        return None

    print()
    print(
        "========================================"
    )

    print(
        f"EXTRACTING: {citation_key}"
    )

    print(
        "========================================"
    )

    print()

    prompt = f"""
Analyze exactly this local PDF:

{pdf_filename}

Expected bibliographic information:

Citation key:
{citation_key}

Title:
{title}

DOI:
{doi}

You MUST inspect the actual PDF using the PDF tools.

Do not rely on bibliographic metadata as technical evidence.

Extract approximately 8-15 high-value scientific claims
from the paper when enough useful material is available.

Focus on information relevant to this engineering review:

- converter topology,
- operating principle,
- DC-link architecture,
- number of converter cells,
- number of machine phases,
- machine winding arrangement,
- semiconductor technology,
- semiconductor voltage rating,
- cell voltage,
- DC-link voltage,
- current,
- power rating,
- switching frequency,
- modulation method,
- semiconductor losses,
- machine losses,
- total efficiency,
- power density,
- balancing,
- common-mode voltage,
- EMI,
- fault tolerance,
- post-fault operation,
- reliability,
- thermal management,
- integrated packaging,
- experimental setup,
- experimental operating conditions,
- limitations,
- future research needs.

For every claim:

1. Use citation key:

   {citation_key}

2. Create claim IDs:

   {citation_key}_C01
   {citation_key}_C02
   {citation_key}_C03
   etc.

3. Give the PDF page number whenever possible.

4. Assign one or more relevant_sections.

5. Record numerical values exactly as reported.

6. Do not estimate unavailable numerical values.

7. Use FULL_TEXT_VERIFIED only when you inspected the
   supporting full text.

8. Keep supporting excerpts short.

Return evidence for this paper only.
"""

    result = await Runner.run(
        evidence_agent,
        prompt,
        max_turns=25,
    )

    database = result.final_output.model_dump()

    papers = database.get(
        "papers",
        []
    )

    if not papers:

        print(
            f"No evidence returned for "
            f"{citation_key}."
        )

        return None

    # We requested exactly one paper.
    extracted = papers[0]

    # Enforce our own known metadata.
    extracted[
        "citation_key"
    ] = citation_key

    extracted[
        "title"
    ] = title

    extracted[
        "pdf_filename"
    ] = pdf_filename

    return extracted


# =========================================================
# MAIN
# =========================================================

async def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Re-extract papers that already "
            "exist in evidence.json."
        ),
    )

    parser.add_argument(
        "--key",
        type=str,
        default=None,
        help=(
            "Extract only one citation key."
        ),
    )

    args = parser.parse_args()

    papers = load_papers_database()

    evidence_database = (
        load_existing_evidence()
    )

    print()
    print(
        "========================================"
    )

    print(
        "AUTOMATIC EVIDENCE EXTRACTION"
    )

    print(
        "========================================"
    )

    print()

    print(
        f"Papers in database: "
        f"{len(papers)}"
    )

    print()

    for paper in papers:

        citation_key = paper.get(
            "citation_key"
        )

        if not citation_key:

            print(
                "Skipping paper without "
                "citation_key."
            )

            continue

        # -----------------------------------------
        # OPTIONAL SINGLE PAPER
        # -----------------------------------------

        if (
            args.key is not None
            and citation_key != args.key
        ):

            continue

        # -----------------------------------------
        # CHECK EXISTING EVIDENCE
        # -----------------------------------------

        existing_index = (
            find_existing_paper(
                evidence_database,
                citation_key,
            )
        )

        if (
            existing_index is not None
            and not args.force
        ):

            print(
                f"Already extracted: "
                f"{citation_key}"
            )

            print(
                "Skipping."
            )

            continue

        # -----------------------------------------
        # EXTRACT
        # -----------------------------------------

        try:

            extracted = (
                await extract_one_paper(
                    paper
                )
            )

        except Exception as error:

            print()
            print(
                f"ERROR extracting "
                f"{citation_key}:"
            )

            print(error)

            print()

            # Continue with the next paper
            # instead of losing all progress.

            continue

        if extracted is None:
            continue

        # -----------------------------------------
        # MERGE
        # -----------------------------------------

        if existing_index is None:

            evidence_database[
                "papers"
            ].append(
                extracted
            )

        else:

            evidence_database[
                "papers"
            ][existing_index] = (
                extracted
            )

        # Save after EVERY paper.
        #
        # This means that if paper 20 fails,
        # results from papers 1-19 remain saved.

        save_evidence(
            evidence_database
        )

        claim_count = len(
            extracted.get(
                "claims",
                []
            )
        )

        print(
            f"Saved {claim_count} claims "
            f"for {citation_key}."
        )

    print()
    print(
        "========================================"
    )

    print(
        "EVIDENCE EXTRACTION COMPLETE"
    )

    print(
        "========================================"
    )

    print()

    print(
        f"Evidence file:\n"
        f"{EVIDENCE_FILE}"
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )