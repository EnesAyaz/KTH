import asyncio
import csv
import json
from pathlib import Path

from dotenv import load_dotenv
from agents import Runner

from paper_agents.figure_agent import (
    figure_agent,
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

COMPARISON_JSON = (
    DATA_DIR
    / "comparison.json"
)

COMPARISON_CSV = (
    DATA_DIR
    / "comparison.csv"
)

FIGURE_PLAN_FILE = (
    DATA_DIR
    / "figure_plan.json"
)


# =========================================================
# ANALYZE CSV COVERAGE
# =========================================================

def analyze_csv():
    """
    Determine which columns exist and how many non-empty
    values each column contains.
    """

    if not COMPARISON_CSV.exists():

        raise FileNotFoundError(
            f"Missing file:\n"
            f"{COMPARISON_CSV}"
        )

    with COMPARISON_CSV.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        rows = list(
            reader
        )

        fieldnames = (
            reader.fieldnames
            or []
        )

    coverage = {}

    for column in fieldnames:

        valid_count = 0

        for row in rows:

            value = row.get(
                column
            )

            if value is None:
                continue

            value = str(
                value
            ).strip()

            if value == "":
                continue

            if value.lower() in [
                "none",
                "null",
                "nan",
            ]:
                continue

            valid_count += 1

        coverage[column] = (
            valid_count
        )

    return {
        "total_rows": len(rows),
        "columns": fieldnames,
        "non_empty_counts": coverage,
    }


# =========================================================
# MAIN
# =========================================================

async def main():

    print()
    print(
        "========================================"
    )
    print(
        "SCIENTIFIC FIGURE PLANNING"
    )
    print(
        "========================================"
    )
    print()

    # -----------------------------------------------------
    # CHECK DATABASE
    # -----------------------------------------------------

    if not COMPARISON_JSON.exists():

        print(
            "comparison.json does not exist."
        )

        print()
        print(
            "Run:"
        )
        print()
        print(
            "python build_comparison.py"
        )

        return

    if not COMPARISON_CSV.exists():

        print(
            "comparison.csv does not exist."
        )

        return

    # -----------------------------------------------------
    # LOAD COMPARISON DATA
    # -----------------------------------------------------

    comparison_data = (
        COMPARISON_JSON.read_text(
            encoding="utf-8"
        )
    )

    coverage = (
        analyze_csv()
    )

    coverage_text = json.dumps(
        coverage,
        indent=2,
        ensure_ascii=False,
    )

    # -----------------------------------------------------
    # DISPLAY COVERAGE
    # -----------------------------------------------------

    print(
        "Database coverage:"
    )
    print()

    for (
        column,
        count,
    ) in coverage[
        "non_empty_counts"
    ].items():

        print(
            f"{column}: {count}"
        )

    print()

    # -----------------------------------------------------
    # AGENT PROMPT
    # -----------------------------------------------------

    prompt = f"""
Design quantitative figures for the review paper.

============================================================
VERIFIED COMPARISON DATABASE
============================================================

{comparison_data}

============================================================
DATABASE COLUMN COVERAGE
============================================================

{coverage_text}

============================================================
TASK
============================================================

Propose approximately 1-6 scientifically useful figures.

IMPORTANT:

Only propose a plot if the necessary numerical columns have
enough non-empty data.

Use ONLY exact database column names permitted by your
schema.

Do not invent generic column names such as:

value
voltage
voltage_v
power
frequency

Prefer minimum_rows = 3 where possible.

If the database is sparse, proposing only one or two figures
is acceptable.

Return structured output only.
"""

    # -----------------------------------------------------
    # RUN AGENT
    # -----------------------------------------------------

    result = await Runner.run(
        figure_agent,
        prompt,
    )

    plan = (
        result.final_output
    )

    data = (
        plan.model_dump()
    )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    FIGURE_PLAN_FILE.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # REPORT
    # -----------------------------------------------------

    print()
    print(
        "========================================"
    )
    print(
        "FIGURE PLAN"
    )
    print(
        "========================================"
    )
    print()

    print(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )
    )

    print()
    print(
        "Figure plan saved:"
    )

    print(
        FIGURE_PLAN_FILE
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )