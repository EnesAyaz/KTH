import asyncio
import csv
import json
from pathlib import Path

from dotenv import load_dotenv
from agents import Runner

from paper_agents.comparison_agent import (
    comparison_agent,
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

EVIDENCE_FILE = (
    DATA_DIR
    / "evidence.json"
)

COMPARISON_JSON_FILE = (
    DATA_DIR
    / "comparison.json"
)

COMPARISON_CSV_FILE = (
    DATA_DIR
    / "comparison.csv"
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

    output = {
        "papers": []
    }

    for paper in data.get(
        "papers",
        []
    ):

        verified_claims = []

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

                verified_claims.append(
                    claim
                )

        if verified_claims:

            output[
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
                        verified_claims,

                    "unresolved_questions":
                        paper.get(
                            "unresolved_questions",
                            [],
                        ),
                }
            )

    return output


# =========================================================
# WRITE CSV
# =========================================================

def write_csv(
    records
):

    fieldnames = [
        "citation_key",
        "title",
        "topology",
        "rated_power_kw",
        "peak_power_kw",
        "dc_link_voltage_v",
        "cell_voltage_v",
        "number_of_cells",
        "number_of_phases",
        "semiconductor_technology",
        "semiconductor_voltage_rating_v",
        "semiconductor_current_rating_a",
        "switching_frequency_khz",
        "efficiency_percent",
        "power_density_kw_per_l",
        "machine_type",
        "winding_configuration",
        "modulation_method",
        "cooling_method",
        "balancing_requirement",
        "common_mode_information",
        "fault_tolerance",
        "post_fault_capability",
        "experimental_level",
        "test_conditions",
        "main_advantages",
        "main_limitations",
        "evidence_claim_ids",
        "missing_information",
    ]

    with COMPARISON_CSV_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for record in records:

            row = dict(record)

            # Convert list fields into readable
            # semicolon-separated CSV strings.

            for field in [
                "main_advantages",
                "main_limitations",
                "evidence_claim_ids",
                "missing_information",
            ]:

                value = row.get(
                    field,
                    []
                )

                if isinstance(
                    value,
                    list
                ):

                    row[field] = (
                        "; ".join(
                            str(item)
                            for item in value
                        )
                    )

            writer.writerow(
                row
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
        "BUILDING COMPARISON DATABASE"
    )

    print(
        "========================================"
    )

    print()

    if not EVIDENCE_FILE.exists():

        print(
            "evidence.json does not exist."
        )

        return

    evidence = (
        load_verified_evidence()
    )

    paper_count = len(
        evidence["papers"]
    )

    print(
        f"Papers with verified evidence: "
        f"{paper_count}"
    )

    if paper_count == 0:

        print(
            "No FULL_TEXT_VERIFIED evidence "
            "available."
        )

        return

    evidence_text = json.dumps(
        evidence,
        indent=2,
        ensure_ascii=False,
    )

    prompt = f"""
Create a standardized comparison database from the
scientific evidence below.

============================================================
FULL-TEXT VERIFIED EVIDENCE
============================================================

{evidence_text}

============================================================
TASK
============================================================

Create one comparison record for each paper where enough
information exists.

Do not invent values.

Use null for unavailable values.

Explicitly list important missing information.

Include evidence_claim_ids so that every populated field
can be traced back to the evidence database.
"""

    result = await Runner.run(
        comparison_agent,
        prompt,
    )

    database = (
        result.final_output
    )

    data = (
        database.model_dump()
    )

    # -----------------------------------------------------
    # SAVE JSON
    # -----------------------------------------------------

    COMPARISON_JSON_FILE.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # SAVE CSV
    # -----------------------------------------------------

    write_csv(
        data["records"]
    )

    print()
    print(
        "Comparison JSON:"
    )

    print(
        COMPARISON_JSON_FILE
    )

    print()

    print(
        "Comparison CSV:"
    )

    print(
        COMPARISON_CSV_FILE
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )