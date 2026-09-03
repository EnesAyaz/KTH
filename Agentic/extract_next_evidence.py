import argparse
import asyncio
import json
import shutil
from pathlib import Path

from dotenv import load_dotenv
from agents import Runner

from paper_agents.evidence_extractor import (
    evidence_agent,
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

PAPERS_DIR = (
    ROOT_DIR
    / "papers"
)

OUTPUT_DIR = (
    ROOT_DIR
    / "output"
)

BACKUP_DIR = (
    DATA_DIR
    / "backups"
)

DOWNLOADED_FILE = (
    DATA_DIR
    / "downloaded_approved_papers.json"
)

PAPERS_DATABASE_FILE = (
    DATA_DIR
    / "papers.json"
)

EVIDENCE_FILE = (
    DATA_DIR
    / "evidence.json"
)

STATUS_REPORT_FILE = (
    OUTPUT_DIR
    / "evidence_extraction_status.md"
)


DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

PAPERS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

BACKUP_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# LOAD JSON
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
# LOAD DOWNLOADED PAPERS
# =========================================================

def load_downloaded_papers():

    if not DOWNLOADED_FILE.exists():

        raise FileNotFoundError(
            f"Could not find:\n"
            f"{DOWNLOADED_FILE}"
        )

    database = load_json(
        DOWNLOADED_FILE,
        {
            "papers": []
        },
    )

    return database.get(
        "papers",
        []
    )


# =========================================================
# LOAD PAPERS DATABASE
# =========================================================

def load_papers_database():

    database = load_json(
        PAPERS_DATABASE_FILE,
        {
            "papers": []
        },
    )

    if isinstance(
        database,
        list,
    ):

        return {
            "papers":
                database
        }

    return database


# =========================================================
# LOAD EVIDENCE DATABASE
# =========================================================

def load_evidence_database():

    database = load_json(
        EVIDENCE_FILE,
        {
            "papers": []
        },
    )

    if not isinstance(
        database,
        dict,
    ):

        return {
            "papers": []
        }

    if "papers" not in database:

        database[
            "papers"
        ] = []

    return database


# =========================================================
# FIND PAPER METADATA
# =========================================================

def find_paper_metadata(
    citation_key,
    papers_database,
):

    for paper in papers_database.get(
        "papers",
        []
    ):

        if (
            paper.get(
                "citation_key"
            )
            == citation_key
        ):

            return paper

    return None


# =========================================================
# FIND EXISTING EVIDENCE
# =========================================================

def find_evidence_index(
    citation_key,
    evidence_database,
):

    for index, paper in enumerate(
        evidence_database.get(
            "papers",
            []
        )
    ):

        if (
            paper.get(
                "citation_key"
            )
            == citation_key
        ):

            return index

    return None


# =========================================================
# COUNT FULL-TEXT CLAIMS
# =========================================================

def count_full_text_claims(
    evidence_paper,
):

    if evidence_paper is None:
        return 0

    return sum(

        1

        for claim in evidence_paper.get(
            "claims",
            []
        )

        if (
            claim.get(
                "verification_level"
            )
            == "FULL_TEXT_VERIFIED"
        )
    )


# =========================================================
# CHECK WHETHER PAPER IS ALREADY PROCESSED
# =========================================================

def already_verified(
    citation_key,
    evidence_database,
):

    index = find_evidence_index(
        citation_key,
        evidence_database,
    )

    if index is None:
        return False

    paper = (
        evidence_database[
            "papers"
        ][index]
    )

    return (
        count_full_text_claims(
            paper
        )
        > 0
    )


# =========================================================
# CREATE EVIDENCE BACKUP
# =========================================================

def backup_evidence(
    citation_key,
):

    if not EVIDENCE_FILE.exists():
        return

    backup_file = (
        BACKUP_DIR
        / (
            f"evidence_before_"
            f"{citation_key}.json"
        )
    )

    shutil.copy2(
        EVIDENCE_FILE,
        backup_file,
    )

    print(
        "Evidence backup:"
    )

    print(
        backup_file
    )

    print()


# =========================================================
# NORMALIZE EXTRACTED PAPER
# =========================================================

def normalize_extracted_paper(
    extracted,
    citation_key,
    title,
    pdf_filename,
):
    """
    Enforce deterministic citation keys and claim IDs.

    The scientific claim content still comes from the
    Evidence Agent.
    """

    extracted[
        "citation_key"
    ] = citation_key

    extracted[
        "title"
    ] = title

    extracted[
        "pdf_filename"
    ] = pdf_filename

    claims = extracted.get(
        "claims",
        []
    )

    for index, claim in enumerate(
        claims,
        start=1,
    ):

        claim[
            "citation_key"
        ] = citation_key

        claim[
            "source_title"
        ] = title

        claim[
            "claim_id"
        ] = (
            f"{citation_key}_C"
            f"{index:02d}"
        )

    return extracted


# =========================================================
# EXTRACT ONE PAPER
# =========================================================

async def extract_paper(
    paper_record,
    metadata,
):

    citation_key = (
        paper_record[
            "citation_key"
        ]
    )

    title = (
        paper_record[
            "title"
        ]
    )

    pdf_filename = (
        paper_record[
            "pdf_filename"
        ]
    )

    pdf_path = (
        PAPERS_DIR
        / pdf_filename
    )

    if not pdf_path.exists():

        raise FileNotFoundError(
            f"PDF not found:\n"
            f"{pdf_path}"
        )

    doi = metadata.get(
        "doi"
    )

    authors = metadata.get(
        "authors",
        []
    )

    year = metadata.get(
        "year"
    )

    journal = metadata.get(
        "journal"
    )

    # -----------------------------------------------------
    # PROMPT
    # -----------------------------------------------------

    prompt = f"""
Analyze exactly this local scientific PDF:

{pdf_filename}

============================================================
KNOWN BIBLIOGRAPHIC METADATA
============================================================

Citation key:
{citation_key}

Title:
{title}

Authors:
{authors}

Year:
{year}

Journal / venue:
{journal}

DOI:
{doi}

============================================================
CRITICAL INSTRUCTION
============================================================

You MUST inspect the actual PDF using the available PDF
tools.

Do NOT treat the bibliographic metadata above as technical
evidence.

Do NOT rely only on the abstract if the body of the paper
is accessible.

Read enough of the complete paper to understand:

- converter architecture,
- methodology,
- experimental setup,
- operating conditions,
- reported quantitative results,
- limitations,
- conclusions.

============================================================
EVIDENCE EXTRACTION TARGET
============================================================

Extract approximately 10-20 high-value scientific claims
when the paper contains enough useful material.

Do not force 20 claims.

Quality and traceability are more important than quantity.

============================================================
PRIORITY INFORMATION
============================================================

Pay particular attention to:

1. Converter topology

2. Number of stacked converter cells

3. Number of machine phases

4. Number and arrangement of machine winding groups

5. Total DC-link voltage

6. Individual cell voltage

7. Semiconductor technology

8. Semiconductor voltage rating

9. Semiconductor current rating

10. Rated converter or motor-drive power

11. Peak power

12. Switching frequency

13. Modulation method

14. Control method

15. DC-link balancing

16. Semiconductor losses

17. Machine losses

18. Total converter efficiency

19. Drive efficiency

20. Power density

21. Cooling method

22. Thermal limitations

23. Common-mode voltage

24. EMI

25. Fault tolerance

26. Post-fault operation

27. Reliability

28. Integrated packaging

29. Experimental validation level

30. Important limitations

============================================================
NUMERICAL CLAIM RULES
============================================================

For every numerical result:

- preserve the exact reported numerical value,
- preserve the unit,
- preserve the associated operating condition,
- identify whether it is measured, simulated, calculated,
  designed, or assumed,
- provide the PDF page number whenever possible.

Do NOT estimate values from graphs.

Do NOT infer missing values using engineering knowledge.

Do NOT calculate new values unless the paper itself reports
the calculation or result.

============================================================
FULL-TEXT VERIFICATION RULE
============================================================

Use:

FULL_TEXT_VERIFIED

only when you have inspected supporting material in the
actual PDF body.

Use:

ABSTRACT_ONLY

only if the claim is supported exclusively by the abstract.

Use:

METADATA_ONLY

only for bibliographic-level information.

The goal of this run is full-text scientific evidence.

============================================================
CLAIM IDS
============================================================

Use:

{citation_key}_C01
{citation_key}_C02
{citation_key}_C03

and continue sequentially.

============================================================
RELEVANT SECTIONS
============================================================

Assign relevant_sections using appropriate review-paper
topics such as:

Introduction

Background and Taxonomy

Converter Architecture

Multiphase Electric Machines

Semiconductor Technology

Modulation and Control

Common-Mode Voltage and EMI

Fault Tolerance

Losses and Efficiency

Integrated Motor Drives

Experimental Validation

System-Level Comparison

Research Gaps

Future Research Directions

Conclusion

============================================================
IMPORTANT SCIENTIFIC DISTINCTIONS
============================================================

Clearly distinguish:

- experimental result,
- simulation result,
- analytical result,
- design target,
- author conclusion,
- limitation,
- future-work statement.

Do not present a design target as a measured result.

Do not present a simulation result as experimental.

Do not present the agent's own interpretation as an author
conclusion.

============================================================
OUTPUT
============================================================

Return evidence for this paper only.

The citation key must be:

{citation_key}
"""

    # -----------------------------------------------------
    # RUN AGENT
    # -----------------------------------------------------

    result = await Runner.run(
        evidence_agent,
        prompt,
        max_turns=30,
    )

    database = (
        result.final_output
        .model_dump()
    )

    extracted_papers = (
        database.get(
            "papers",
            []
        )
    )

    if not extracted_papers:

        raise RuntimeError(
            "Evidence Agent returned no paper evidence."
        )

    extracted = (
        extracted_papers[0]
    )

    extracted = (
        normalize_extracted_paper(
            extracted,
            citation_key,
            title,
            pdf_filename,
        )
    )

    return extracted


# =========================================================
# MERGE EVIDENCE
# =========================================================

def merge_evidence(
    evidence_database,
    extracted,
):

    citation_key = (
        extracted[
            "citation_key"
        ]
    )

    existing_index = (
        find_evidence_index(
            citation_key,
            evidence_database,
        )
    )

    if existing_index is None:

        evidence_database[
            "papers"
        ].append(
            extracted
        )

        return "ADDED"

    evidence_database[
        "papers"
    ][existing_index] = (
        extracted
    )

    return "REPLACED"


# =========================================================
# BUILD STATUS REPORT
# =========================================================

def create_status_report(
    downloaded_papers,
    evidence_database,
):

    lines = []

    lines.append(
        "# Evidence Extraction Status"
    )

    lines.append("")

    lines.append(
        "| Citation Key | PDF | Full-Text Claims | Status |"
    )

    lines.append(
        "|---|---|---:|---|"
    )

    for paper in downloaded_papers:

        citation_key = (
            paper[
                "citation_key"
            ]
        )

        pdf_filename = (
            paper[
                "pdf_filename"
            ]
        )

        index = find_evidence_index(
            citation_key,
            evidence_database,
        )

        if index is None:

            claim_count = 0

            status = (
                "PENDING"
            )

        else:

            evidence_paper = (
                evidence_database[
                    "papers"
                ][index]
            )

            claim_count = (
                count_full_text_claims(
                    evidence_paper
                )
            )

            if claim_count > 0:

                status = (
                    "FULL_TEXT_VERIFIED"
                )

            else:

                status = (
                    "NO FULL-TEXT CLAIMS"
                )

        lines.append(
            f"| `{citation_key}` "
            f"| `{pdf_filename}` "
            f"| {claim_count} "
            f"| {status} |"
        )

    STATUS_REPORT_FILE.write_text(
        "\n".join(
            lines
        )
        + "\n",
        encoding="utf-8",
    )


# =========================================================
# SELECT PAPER
# =========================================================

def select_paper(
    downloaded_papers,
    evidence_database,
    requested_key,
    force,
):

    # -----------------------------------------------------
    # EXPLICIT CITATION KEY
    # -----------------------------------------------------

    if requested_key:

        for paper in downloaded_papers:

            if (
                paper[
                    "citation_key"
                ]
                == requested_key
            ):

                if (
                    already_verified(
                        requested_key,
                        evidence_database,
                    )
                    and not force
                ):

                    raise RuntimeError(
                        f"{requested_key} already has "
                        f"FULL_TEXT_VERIFIED evidence.\n"
                        f"Use --force to re-extract it."
                    )

                return paper

        raise RuntimeError(
            f"Citation key not found in downloaded "
            f"approved papers: {requested_key}"
        )

    # -----------------------------------------------------
    # AUTOMATICALLY SELECT NEXT PENDING PAPER
    # -----------------------------------------------------

    for paper in downloaded_papers:

        citation_key = (
            paper[
                "citation_key"
            ]
        )

        if not already_verified(
            citation_key,
            evidence_database,
        ):

            return paper

    return None


# =========================================================
# MAIN
# =========================================================

async def main():

    parser = argparse.ArgumentParser(
        description=(
            "Extract full-text scientific evidence from "
            "one approved downloaded paper."
        )
    )

    parser.add_argument(
        "--key",
        type=str,
        default=None,
        help=(
            "Citation key to process, for example "
            "Rohner2024."
        ),
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Replace existing full-text evidence for "
            "the selected paper."
        ),
    )

    args = parser.parse_args()

    print()
    print(
        "========================================"
    )

    print(
        "SINGLE-PAPER EVIDENCE EXTRACTION"
    )

    print(
        "========================================"
    )

    print()

    # -----------------------------------------------------
    # LOAD DATABASES
    # -----------------------------------------------------

    try:

        downloaded_papers = (
            load_downloaded_papers()
        )

    except FileNotFoundError as error:

        print(error)

        return

    papers_database = (
        load_papers_database()
    )

    evidence_database = (
        load_evidence_database()
    )

    # -----------------------------------------------------
    # SELECT PAPER
    # -----------------------------------------------------

    try:

        selected = select_paper(
            downloaded_papers,
            evidence_database,
            args.key,
            args.force,
        )

    except RuntimeError as error:

        print(error)

        return

    if selected is None:

        print(
            "All downloaded approved papers already "
            "contain FULL_TEXT_VERIFIED evidence."
        )

        create_status_report(
            downloaded_papers,
            evidence_database,
        )

        return

    citation_key = (
        selected[
            "citation_key"
        ]
    )

    title = (
        selected[
            "title"
        ]
    )

    pdf_filename = (
        selected[
            "pdf_filename"
        ]
    )

    # -----------------------------------------------------
    # METADATA
    # -----------------------------------------------------

    metadata = find_paper_metadata(
        citation_key,
        papers_database,
    )

    if metadata is None:

        print(
            "ERROR:"
        )

        print(
            f"{citation_key} is not present "
            f"in papers.json."
        )

        return

    # -----------------------------------------------------
    # CHECK PDF
    # -----------------------------------------------------

    pdf_path = (
        PAPERS_DIR
        / pdf_filename
    )

    if not pdf_path.exists():

        print(
            "ERROR:"
        )

        print(
            "PDF does not exist:"
        )

        print(
            pdf_path
        )

        return

    # -----------------------------------------------------
    # DISPLAY PAPER
    # -----------------------------------------------------

    print(
        f"Citation key: "
        f"{citation_key}"
    )

    print()

    print(
        f"Title:"
    )

    print(
        title
    )

    print()

    print(
        f"PDF:"
    )

    print(
        pdf_path
    )

    print()

    # -----------------------------------------------------
    # BACKUP
    # -----------------------------------------------------

    backup_evidence(
        citation_key
    )

    # -----------------------------------------------------
    # EXTRACT
    # -----------------------------------------------------

    print(
        "Running Evidence Extractor..."
    )

    print()

    try:

        extracted = await extract_paper(
            selected,
            metadata,
        )

    except Exception as error:

        print()
        print(
            "========================================"
        )

        print(
            "EXTRACTION FAILED"
        )

        print(
            "========================================"
        )

        print()

        print(error)

        return

    # -----------------------------------------------------
    # VALIDATE RESULT
    # -----------------------------------------------------

    total_claims = len(
        extracted.get(
            "claims",
            []
        )
    )

    full_text_claims = (
        count_full_text_claims(
            extracted
        )
    )

    abstract_claims = sum(

        1

        for claim in extracted.get(
            "claims",
            []
        )

        if (
            claim.get(
                "verification_level"
            )
            == "ABSTRACT_ONLY"
        )
    )

    metadata_claims = sum(

        1

        for claim in extracted.get(
            "claims",
            []
        )

        if (
            claim.get(
                "verification_level"
            )
            == "METADATA_ONLY"
        )
    )

    print()
    print(
        "EXTRACTION RESULT"
    )

    print(
        "----------------------------------------"
    )

    print(
        f"Total claims:          "
        f"{total_claims}"
    )

    print(
        f"FULL_TEXT_VERIFIED:    "
        f"{full_text_claims}"
    )

    print(
        f"ABSTRACT_ONLY:         "
        f"{abstract_claims}"
    )

    print(
        f"METADATA_ONLY:         "
        f"{metadata_claims}"
    )

    print()

    # -----------------------------------------------------
    # REQUIRE FULL-TEXT EVIDENCE
    # -----------------------------------------------------

    if full_text_claims == 0:

        print(
            "REJECTED:"
        )

        print()

        print(
            "The Evidence Agent did not produce any "
            "FULL_TEXT_VERIFIED claims."
        )

        print()

        print(
            "evidence.json was NOT modified."
        )

        return

    # -----------------------------------------------------
    # MERGE
    # -----------------------------------------------------

    merge_status = (
        merge_evidence(
            evidence_database,
            extracted,
        )
    )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    EVIDENCE_FILE.write_text(
        json.dumps(
            evidence_database,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # STATUS REPORT
    # -----------------------------------------------------

    create_status_report(
        downloaded_papers,
        evidence_database,
    )

    # -----------------------------------------------------
    # SUCCESS
    # -----------------------------------------------------

    print(
        "========================================"
    )

    print(
        "EVIDENCE EXTRACTION SUCCESSFUL"
    )

    print(
        "========================================"
    )

    print()

    print(
        f"Paper: {citation_key}"
    )

    print(
        f"Database action: "
        f"{merge_status}"
    )

    print(
        f"FULL_TEXT_VERIFIED claims: "
        f"{full_text_claims}"
    )

    print()

    print(
        "Evidence database:"
    )

    print(
        EVIDENCE_FILE
    )

    print()

    print(
        "Status report:"
    )

    print(
        STATUS_REPORT_FILE
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "Inspect the extracted evidence before "
        "processing the next paper."
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )