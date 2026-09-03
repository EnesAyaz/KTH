import csv
from pathlib import Path


# =========================================================
# PROJECT PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

CSV_FILE = (
    ROOT_DIR
    / "data"
    / "comparison.csv"
)


# =========================================================
# NUMERICAL COLUMNS WE CARE ABOUT
# =========================================================

NUMERIC_COLUMNS = [
    "rated_power_kw",
    "peak_power_kw",
    "dc_link_voltage_v",
    "cell_voltage_v",
    "number_of_cells",
    "number_of_phases",
    "semiconductor_voltage_rating_v",
    "semiconductor_current_rating_a",
    "switching_frequency_khz",
    "efficiency_percent",
    "power_density_kw_per_l",
]


# =========================================================
# CHECK WHETHER A VALUE IS VALID NUMERIC DATA
# =========================================================

def has_numeric_value(value):
    """
    Return True only when the value can actually be
    interpreted as a numerical value.
    """

    if value is None:
        return False

    text = str(value).strip()

    if text == "":
        return False

    if text.lower() in [
        "none",
        "null",
        "nan",
        "n/a",
        "--",
    ]:
        return False

    try:
        float(text)
        return True

    except ValueError:
        return False


# =========================================================
# COUNT VALID VALUES IN ONE COLUMN
# =========================================================

def count_valid_values(rows, column):
    """
    Count how many comparison records contain usable
    numerical data in the requested column.
    """

    return sum(
        1
        for row in rows
        if has_numeric_value(
            row.get(column)
        )
    )


# =========================================================
# COUNT VALID PAIRED VALUES
# =========================================================

def count_valid_pairs(
    rows,
    x_column,
    y_column,
):
    """
    Count how many papers contain BOTH x and y values.

    This is what matters for scatter plots.
    """

    return sum(
        1
        for row in rows
        if (
            has_numeric_value(
                row.get(x_column)
            )
            and
            has_numeric_value(
                row.get(y_column)
            )
        )
    )


# =========================================================
# FIGURE QUALITY CLASSIFICATION
# =========================================================

def classify_pair(count):
    """
    Give a simple scientific usefulness classification.
    """

    if count >= 10:
        return "STRONG FIGURE CANDIDATE"

    if count >= 5:
        return "GOOD FIGURE CANDIDATE"

    if count >= 3:
        return "POSSIBLE FIGURE"

    if count == 2:
        return "WEAK - MORE DATA NEEDED"

    if count == 1:
        return "INSUFFICIENT"

    return "NO DATA"


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print(
        "========================================"
    )
    print(
        "COMPARISON DATABASE COVERAGE"
    )
    print(
        "========================================"
    )
    print()

    # -----------------------------------------------------
    # CHECK FILE
    # -----------------------------------------------------

    if not CSV_FILE.exists():

        print(
            "ERROR:"
        )

        print(
            "comparison.csv does not exist."
        )

        print()
        print(
            f"Expected location:"
        )

        print(
            CSV_FILE
        )

        print()
        print(
            "Run this first:"
        )

        print()
        print(
            "python build_comparison.py"
        )

        return

    # -----------------------------------------------------
    # READ CSV
    # -----------------------------------------------------

    with CSV_FILE.open(
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

        columns = (
            reader.fieldnames
            or []
        )

    print(
        f"Comparison records: {len(rows)}"
    )

    print()

    # -----------------------------------------------------
    # DISPLAY AVAILABLE COLUMNS
    # -----------------------------------------------------

    print(
        "AVAILABLE CSV COLUMNS"
    )

    print(
        "----------------------------------------"
    )

    for column in columns:

        print(
            f"  {column}"
        )

    print()

    # -----------------------------------------------------
    # NUMERICAL COVERAGE
    # -----------------------------------------------------

    print(
        "========================================"
    )
    print(
        "NUMERICAL DATA COVERAGE"
    )
    print(
        "========================================"
    )
    print()

    print(
        f"{'Column':45}"
        f"{'Valid':>8}"
        f"{'Coverage':>12}"
    )

    print(
        "-" * 65
    )

    for column in NUMERIC_COLUMNS:

        valid = count_valid_values(
            rows,
            column,
        )

        if len(rows) > 0:

            percentage = (
                100
                * valid
                / len(rows)
            )

        else:

            percentage = 0.0

        print(
            f"{column:45}"
            f"{valid:>8}"
            f"{percentage:>11.1f}%"
        )

    print()

    # -----------------------------------------------------
    # IMPORTANT FIGURE PAIRS
    # -----------------------------------------------------

    figure_pairs = [
        (
            "number_of_cells",
            "semiconductor_voltage_rating_v",
            "Device voltage rating vs number of cells",
        ),
        (
            "dc_link_voltage_v",
            "semiconductor_voltage_rating_v",
            "Device voltage rating vs DC-link voltage",
        ),
        (
            "semiconductor_voltage_rating_v",
            "switching_frequency_khz",
            "Switching frequency vs device voltage rating",
        ),
        (
            "switching_frequency_khz",
            "efficiency_percent",
            "Efficiency vs switching frequency",
        ),
        (
            "power_density_kw_per_l",
            "efficiency_percent",
            "Efficiency vs power density",
        ),
        (
            "number_of_cells",
            "number_of_phases",
            "Number of phases vs number of cells",
        ),
        (
            "rated_power_kw",
            "dc_link_voltage_v",
            "Rated power vs DC-link voltage",
        ),
    ]

    print(
        "========================================"
    )
    print(
        "POSSIBLE FIGURE PAIRS"
    )
    print(
        "========================================"
    )
    print()

    for (
        x_column,
        y_column,
        description,
    ) in figure_pairs:

        paired_count = count_valid_pairs(
            rows,
            x_column,
            y_column,
        )

        status = classify_pair(
            paired_count
        )

        print(
            description
        )

        print(
            f"  X column: {x_column}"
        )

        print(
            f"  Y column: {y_column}"
        )

        print(
            f"  Paired records: {paired_count}"
        )

        print(
            f"  Status: {status}"
        )

        print()

    # -----------------------------------------------------
    # PAPER-BY-PAPER COVERAGE
    # -----------------------------------------------------

    print(
        "========================================"
    )
    print(
        "PAPER-BY-PAPER COVERAGE"
    )
    print(
        "========================================"
    )
    print()

    if not rows:

        print(
            "No comparison records available."
        )

        return

    for row in rows:

        citation_key = (
            row.get(
                "citation_key"
            )
            or "UNKNOWN"
        )

        print(
            f"[{citation_key}]"
        )

        numerical_fields = []

        for column in NUMERIC_COLUMNS:

            value = row.get(
                column
            )

            if has_numeric_value(
                value
            ):

                numerical_fields.append(
                    (
                        column,
                        value,
                    )
                )

        if numerical_fields:

            for (
                column,
                value,
            ) in numerical_fields:

                print(
                    f"  {column}: {value}"
                )

        else:

            print(
                "  No usable numerical fields."
            )

        print()

    # -----------------------------------------------------
    # FINAL INTERPRETATION
    # -----------------------------------------------------

    print(
        "========================================"
    )
    print(
        "INTERPRETATION"
    )
    print(
        "========================================"
    )
    print()

    print(
        "Use this report to decide whether:"
    )

    print()

    print(
        "1. We already have enough data for figures,"
    )

    print(
        "or"
    )

    print(
        "2. We need additional papers / evidence first."
    )

    print()

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()