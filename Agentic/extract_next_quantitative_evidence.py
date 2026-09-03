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

DATA_DIR = ROOT_DIR / "data"

PAPERS_DIR = ROOT_DIR / "papers"

OUTPUT_DIR = ROOT_DIR / "output"

BACKUP_DIR = (
    DATA_DIR
    / "backups"
)

MANIFEST_FILE = (
    DATA_DIR
    / "downloaded_quantitative_papers.json"
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
    / "quantitative_evidence_extraction_status.md"
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
# JSON UTILITIES
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
# LOAD SECOND-ROUND MANIFEST
# =========================================================

def load_manifest():

    if not MANIFEST_FILE.exists():

        raise FileNotFoundError(
            f"Could not find:\n"
            f"{MANIFEST_FILE}\n\n"
            f"Run first:\n"
            f"python ingest_quantitative_candidates.py"
        )

    database = load_json(
        MANIFEST_FILE,
        {
            "papers": []
        },
    )

    papers = database.get(
        "papers",
        []
    )

    if not papers:

        raise RuntimeError(
            "The quantitative extraction manifest "
            "contains no papers."
        )

    return papers


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
# FIND EVIDENCE ENTRY
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
# ALREADY VERIFIED?
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

    evidence_paper = (
        evidence_database[
            "papers"
        ][index]
    )

    return (
        count_full_text_claims(
            evidence_paper
        )
        > 0
    )


# =========================================================
# BACKUP
# =========================================================

def backup_evidence(
    citation_key,
):

    if not EVIDENCE_FILE.exists():
        return None

    backup_file = (
        BACKUP_DIR
        / (
            f"evidence_before_quantitative_"
            f"{citation_key}.json"
        )
    )

    shutil.copy2(
        EVIDENCE_FILE,
        backup_file,
    )

    return backup_file


# =========================================================
# NORMALIZE OUTPUT
# =========================================================

def normalize_extracted_paper(
    extracted,
    citation_key,
    title,
    pdf_filename,
):

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
# BUILD EXTRACTION PROMPT
# =========================================================

def build_prompt(
    citation_key,
    title,
    pdf_filename,
    metadata,
):

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

    discovery_metadata = metadata.get(
        "discovery_metadata",
        {}
    )

    expected_fields = (
        discovery_metadata.get(
            "expected_quantitative_fields",
            []
        )
        or []
    )

    expected_pairs = (
        discovery_metadata.get(
            "matched_quantitative_pairs",
            []
        )
        or []
    )

    return f"""
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
DISCOVERY-STAGE TARGETS
============================================================

The literature-discovery system suggested that this paper
MAY contain the following useful quantitative fields:

{expected_fields}

Potential comparison pairs:

{expected_pairs}

IMPORTANT:

These are discovery-stage expectations only.

They are NOT scientific evidence.

They may be wrong.

Do NOT populate a claim simply because a field appears in
this list.

Every extracted claim must be supported by the actual PDF.

============================================================
CRITICAL FULL-TEXT INSTRUCTION
============================================================

You MUST inspect the actual local PDF using the available
PDF-reading tools.

Do NOT use bibliographic metadata as technical evidence.

Do NOT rely solely on the abstract when the body of the
paper is available.

Read enough of the complete paper to understand:

- converter architecture,
- system architecture,
- experimental setup,
- operating conditions,
- semiconductor devices,
- thermal system,
- measured performance,
- reported limitations,
- conclusions.

============================================================
HIGH-PRIORITY QUANTITATIVE TARGETS
============================================================

Pay particular attention to:

1. rated_power_kw

2. peak_power_kw

3. dc_link_voltage_v

4. cell_voltage_v

5. number_of_cells

6. number_of_phases

7. semiconductor_voltage_rating_v

8. semiconductor_current_rating_a

9. switching_frequency_khz

10. efficiency_percent

11. power_density_kw_per_l

12. cooling_method

============================================================
OTHER SCIENTIFIC TARGETS
============================================================

Also extract useful evidence concerning:

- topology,
- winding arrangement,
- machine type,
- modulation,
- control,
- balancing,
- semiconductor losses,
- machine losses,
- thermal limitations,
- common-mode voltage,
- EMI,
- fault tolerance,
- post-fault operation,
- reliability,
- integrated packaging,
- experimental validation,
- major limitations.

============================================================
NUMERICAL CLAIM RULES
============================================================

For every numerical claim:

- preserve the reported numerical value,
- preserve its unit,
- preserve operating conditions,
- identify whether the result is measured,
  simulated, calculated, designed, assumed,
  targeted, or estimated by the paper authors,
- provide the PDF page number whenever possible.

DO NOT estimate numbers from graphs.

DO NOT visually interpolate plots.

DO NOT calculate missing values yourself.

DO NOT infer semiconductor voltage rating from DC-link
voltage.

DO NOT infer cell voltage from total DC-link voltage unless
the paper explicitly states the relationship.

DO NOT infer efficiency from device technology.

DO NOT infer power density from dimensions unless the paper
itself explicitly defines/calculates the power-density
metric.

============================================================
POWER DENSITY RULE
============================================================

Power density is a high-priority database gap.

However, extract a power-density claim ONLY if the paper
explicitly reports it or explicitly performs the
calculation.

Record what the metric refers to when available, for
example:

- inverter only,
- converter module,
- integrated drive,
- power electronics,
- complete motor-drive system.

Do not treat these definitions as interchangeable.

============================================================
EFFICIENCY RULE
============================================================

When extracting efficiency, preserve the distinction
between:

- measured efficiency,
- simulated efficiency,
- calculated efficiency,
- peak efficiency,
- rated-point efficiency,
- inverter efficiency,
- drive efficiency,
- system efficiency.

Do not collapse different efficiency definitions into one
claim.

============================================================
CELL DEFINITION RULE
============================================================

Be especially careful with:

number_of_cells

A stacked-polyphase-bridge series converter cell is not
automatically equivalent to:

- one inverter module,
- one phase leg,
- one machine segment,
- one integrated drive module,
- one power-electronic building block.

Only describe something as an SPB converter cell if the
paper supports that interpretation.

============================================================
ABSENCE CLAIM RULE
============================================================

DO NOT create broad negative claims such as:

"The paper does not report efficiency, power density,
device rating, EMI, cooling..."

Absence from your extracted evidence is sufficient.

If a field cannot be located reliably, simply do not
extract a claim for that field.

Only create a limitation claim when the authors themselves
explicitly discuss that limitation or when a specific
limitation is directly supported by identifiable text.

============================================================
EVIDENCE EXTRACTION TARGET
============================================================

Extract approximately 10-20 high-value claims when the
paper contains enough useful material.

Do not force a specific number.

Quality and traceability are more important than quantity.

============================================================
FULL-TEXT VERIFICATION
============================================================

Use:

FULL_TEXT_VERIFIED

only when you inspected supporting material in the actual
PDF body.

Use:

ABSTRACT_ONLY

only if support comes exclusively from the abstract.

Use:

METADATA_ONLY

only for bibliographic information.

The objective of this run is FULL_TEXT_VERIFIED scientific
evidence.

============================================================
CLAIM IDS
============================================================

Use sequential IDs:

{citation_key}_C01
{citation_key}_C02
{citation_key}_C03

and continue sequentially.

============================================================
RELEVANT REVIEW SECTIONS
============================================================

Use relevant_sections such as:

Introduction

Background and Taxonomy

Converter Architecture

Multiphase Electric Machines

Semiconductor Technology

Modulation and Control

Common-Mode Voltage and EMI

Fault Tolerance

Losses and Efficiency

Power Density

Thermal Management

Integrated Motor Drives

Experimental Validation

System-Level Comparison

Research Gaps

Future Research Directions

Conclusion

============================================================
SCIENTIFIC DISTINCTIONS
============================================================

Clearly distinguish:

- experimental result,
- simulation result,
- analytical result,
- design target,
- calculated result,
- author conclusion,
- author-stated limitation,
- future work.

Do not present simulation as measurement.

Do not present a target as an achieved result.

Do not present your own interpretation as an author
conclusion.

============================================================
OUTPUT
============================================================

Return evidence for THIS PAPER ONLY.

The citation key must be exactly:

{citation_key}
"""


# =========================================================
# EXTRACT ONE PAPER
# =========================================================

async def extract_paper(
    manifest_record,
    metadata,
):

    citation_key = (
        manifest_record[
            "citation_key"
        ]
    )

    title = (
        manifest_record[
            "title"
        ]
    )

    pdf_filename = (
        manifest_record[
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

    prompt = build_prompt(
        citation_key,
        title,
        pdf_filename,
        metadata,
    )

    result = await Runner.run(
        evidence_agent,
        prompt,
        max_turns=30,
    )

    output = (
        result.final_output
        .model_dump()
    )

    extracted_papers = (
        output.get(
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

    return normalize_extracted_paper(
        extracted,
        citation_key,
        title,
        pdf_filename,
    )


# =========================================================
# MERGE
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

    index = find_evidence_index(
        citation_key,
        evidence_database,
    )

    if index is None:

        evidence_database[
            "papers"
        ].append(
            extracted
        )

        return "ADDED"

    evidence_database[
        "papers"
    ][index] = extracted

    return "REPLACED"


# =========================================================
# STATUS REPORT
# =========================================================

def create_status_report(
    manifest,
    evidence_database,
):

    lines = []

    lines.append(
        "# Quantitative Evidence Extraction Status"
    )

    lines.append("")

    lines.append(
        "| Citation Key | PDF | Full-Text Claims | Status |"
    )

    lines.append(
        "|---|---|---:|---|"
    )

    for paper in manifest:

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

            count = 0

            status = "PENDING"

        else:

            evidence_paper = (
                evidence_database[
                    "papers"
                ][index]
            )

            count = (
                count_full_text_claims(
                    evidence_paper
                )
            )

            if count > 0:

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
            f"| {count} "
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
# SELECT NEXT PAPER
# =========================================================

def select_paper(
    manifest,
    evidence_database,
    requested_key,
    force,
):

    if requested_key:

        for paper in manifest:

            if (
                paper.get(
                    "citation_key"
                )
                != requested_key
            ):

                continue

            if (
                already_verified(
                    requested_key,
                    evidence_database,
                )
                and
                not force
            ):

                raise RuntimeError(
                    f"{requested_key} already contains "
                    f"FULL_TEXT_VERIFIED evidence.\n"
                    f"Use --force only if you truly "
                    f"want to replace it."
                )

            return paper

        raise RuntimeError(
            f"Citation key not found in second-round "
            f"manifest: {requested_key}"
        )

    # Automatically choose first pending paper.
    for paper in manifest:

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
            "Extract full-text evidence from one "
            "second-round quantitative paper."
        )
    )

    parser.add_argument(
        "--key",
        type=str,
        default=None,
        help=(
            "Optional citation key. If omitted, the "
            "first pending second-round paper is used."
        ),
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Replace existing evidence for the selected "
            "paper."
        ),
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help=(
            "Show second-round paper status without "
            "running the Evidence Agent."
        ),
    )

    args = parser.parse_args()

    print()
    print(
        "========================================"
    )

    print(
        "SECOND-ROUND EVIDENCE EXTRACTION"
    )

    print(
        "========================================"
    )

    print()

    # -----------------------------------------------------
    # LOAD
    # -----------------------------------------------------

    try:

        manifest = load_manifest()

    except Exception as error:

        print(
            "ERROR:"
        )

        print(error)

        return

    papers_database = (
        load_papers_database()
    )

    evidence_database = (
        load_evidence_database()
    )

    # -----------------------------------------------------
    # LIST MODE
    # -----------------------------------------------------

    if args.list:

        print(
            "SECOND-ROUND PAPERS"
        )

        print(
            "----------------------------------------"
        )

        for paper in manifest:

            citation_key = (
                paper[
                    "citation_key"
                ]
            )

            if already_verified(
                citation_key,
                evidence_database,
            ):

                index = find_evidence_index(
                    citation_key,
                    evidence_database,
                )

                count = (
                    count_full_text_claims(
                        evidence_database[
                            "papers"
                        ][index]
                    )
                )

                status = (
                    f"VERIFIED ({count} claims)"
                )

            else:

                status = "PENDING"

            print(
                f"{citation_key:25s} "
                f"{status}"
            )

        print()

        create_status_report(
            manifest,
            evidence_database,
        )

        return

    # -----------------------------------------------------
    # SELECT PAPER
    # -----------------------------------------------------

    try:

        selected = select_paper(
            manifest,
            evidence_database,
            args.key,
            args.force,
        )

    except RuntimeError as error:

        print(
            "ERROR:"
        )

        print(error)

        return

    if selected is None:

        print(
            "All second-round papers already contain "
            "FULL_TEXT_VERIFIED evidence."
        )

        create_status_report(
            manifest,
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
            f"{citation_key} is not present in "
            f"papers.json."
        )

        return

    # -----------------------------------------------------
    # PDF
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
    # DISPLAY
    # -----------------------------------------------------

    print(
        f"Citation key: "
        f"{citation_key}"
    )

    print()

    print(
        "Title:"
    )

    print(
        title
    )

    print()

    print(
        "PDF:"
    )

    print(
        pdf_path
    )

    print()

    # -----------------------------------------------------
    # BACKUP
    # -----------------------------------------------------

    backup_file = backup_evidence(
        citation_key
    )

    if backup_file:

        print(
            "Evidence backup:"
        )

        print(
            backup_file
        )

        print()

    # -----------------------------------------------------
    # RUN AGENT
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
    # COUNTS
    # -----------------------------------------------------

    claims = extracted.get(
        "claims",
        []
    )

    total_claims = len(
        claims
    )

    full_text_claims = (
        count_full_text_claims(
            extracted
        )
    )

    abstract_claims = sum(
        1
        for claim in claims
        if (
            claim.get(
                "verification_level"
            )
            == "ABSTRACT_ONLY"
        )
    )

    metadata_claims = sum(
        1
        for claim in claims
        if (
            claim.get(
                "verification_level"
            )
            == "METADATA_ONLY"
        )
    )

    numerical_claims = sum(
        1
        for claim in claims
        if (
            claim.get(
                "numerical_values",
                []
            )
        )
    )

    # -----------------------------------------------------
    # DISPLAY EXTRACTION RESULT
    # -----------------------------------------------------

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

    print(
        f"Numerical claims:      "
        f"{numerical_claims}"
    )

    print()

    # -----------------------------------------------------
    # REQUIRE ACTUAL FULL TEXT
    # -----------------------------------------------------

    if full_text_claims == 0:

        print(
            "REJECTED:"
        )

        print()

        print(
            "No FULL_TEXT_VERIFIED evidence was "
            "produced."
        )

        print()

        print(
            "evidence.json was NOT modified."
        )

        return

    # -----------------------------------------------------
    # MERGE
    # -----------------------------------------------------

    merge_status = merge_evidence(
        evidence_database,
        extracted,
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
        manifest,
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
        f"Paper: "
        f"{citation_key}"
    )

    print(
        f"Database action: "
        f"{merge_status}"
    )

    print(
        f"FULL_TEXT_VERIFIED claims: "
        f"{full_text_claims}"
    )

    print(
        f"Numerical claims: "
        f"{numerical_claims}"
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
        "Second-round status report:"
    )

    print(
        STATUS_REPORT_FILE
    )

    print()

    print(
        "NEXT:"
    )

    print()

    print(
        f"python check_evidence_quality.py "
        f"--key {citation_key}"
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )