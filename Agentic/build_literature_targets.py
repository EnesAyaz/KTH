import csv
import json
from pathlib import Path


# =========================================================
# PROJECT PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

DATA_DIR = (
    ROOT_DIR
    / "data"
)

OUTPUT_DIR = (
    ROOT_DIR
    / "output"
)

COMPARISON_FILE = (
    DATA_DIR
    / "comparison.csv"
)

EVIDENCE_FILE = (
    DATA_DIR
    / "evidence.json"
)

JSON_OUTPUT_FILE = (
    DATA_DIR
    / "literature_targets.json"
)

REPORT_FILE = (
    OUTPUT_DIR
    / "literature_targets.md"
)


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# TARGET NUMERICAL FIELDS
# =========================================================

NUMERICAL_TARGETS = {

    "rated_power_kw": {
        "minimum": 5,
        "description":
            "Rated experimental converter or drive power",
    },

    "peak_power_kw": {
        "minimum": 3,
        "description":
            "Peak or short-duration power rating",
    },

    "dc_link_voltage_v": {
        "minimum": 5,
        "description":
            "DC-link voltage",
    },

    "cell_voltage_v": {
        "minimum": 5,
        "description":
            "Voltage handled by an individual converter cell",
    },

    "number_of_cells": {
        "minimum": 5,
        "description":
            "Number of stacked converter cells",
    },

    "number_of_phases": {
        "minimum": 5,
        "description":
            "Number of machine phases or winding groups",
    },

    "semiconductor_voltage_rating_v": {
        "minimum": 5,
        "description":
            "Semiconductor blocking-voltage rating",
    },

    "semiconductor_current_rating_a": {
        "minimum": 3,
        "description":
            "Semiconductor current rating",
    },

    "switching_frequency_khz": {
        "minimum": 5,
        "description":
            "Converter switching frequency",
    },

    "efficiency_percent": {
        "minimum": 5,
        "description":
            "Measured converter or drive efficiency",
    },

    "power_density_kw_per_l": {
        "minimum": 3,
        "description":
            "Reported converter or drive power density",
    },
}


# =========================================================
# IMPORTANT PAIRED COMPARISONS
# =========================================================

PAIR_TARGETS = [

    {
        "name":
            "Device voltage rating vs number of cells",

        "x":
            "number_of_cells",

        "y":
            "semiconductor_voltage_rating_v",

        "minimum":
            5,

        "purpose":
            (
                "Demonstrate semiconductor voltage scaling "
                "enabled by converter stacking."
            ),
    },

    {
        "name":
            "Device voltage rating vs DC-link voltage",

        "x":
            "dc_link_voltage_v",

        "y":
            "semiconductor_voltage_rating_v",

        "minimum":
            5,

        "purpose":
            (
                "Compare system DC voltage with the voltage "
                "class of semiconductor devices."
            ),
    },

    {
        "name":
            "Switching frequency vs semiconductor voltage",

        "x":
            "semiconductor_voltage_rating_v",

        "y":
            "switching_frequency_khz",

        "minimum":
            5,

        "purpose":
            (
                "Investigate whether lower-voltage devices "
                "are associated with higher reported "
                "switching frequencies."
            ),
    },

    {
        "name":
            "Efficiency vs switching frequency",

        "x":
            "switching_frequency_khz",

        "y":
            "efficiency_percent",

        "minimum":
            5,

        "purpose":
            (
                "Compare reported efficiency with switching "
                "frequency while preserving the operating "
                "conditions reported by each source."
            ),
    },

    {
        "name":
            "Efficiency vs power density",

        "x":
            "power_density_kw_per_l",

        "y":
            "efficiency_percent",

        "minimum":
            5,

        "purpose":
            (
                "Assess the reported efficiency and "
                "power-density tradeoff."
            ),
    },

    {
        "name":
            "Rated power vs DC-link voltage",

        "x":
            "dc_link_voltage_v",

        "y":
            "rated_power_kw",

        "minimum":
            5,

        "purpose":
            (
                "Show the experimental scale of reported "
                "converter and motor-drive demonstrations."
            ),
    },
]


# =========================================================
# REVIEW TOPICS
# =========================================================

REVIEW_TOPICS = [

    {
        "topic":
            "Stacked polyphase bridge architecture",

        "priority_fields": [
            "dc_link_voltage_v",
            "cell_voltage_v",
            "number_of_cells",
            "number_of_phases",
        ],

        "desired_information": [
            "DC-side series stacking arrangement",
            "number of bridge cells",
            "machine phase or winding-group arrangement",
            "cell voltage",
            "total DC-link voltage",
            "experimental validation",
        ],
    },

    {
        "topic":
            "Semiconductor voltage scaling",

        "priority_fields": [
            "semiconductor_voltage_rating_v",
            "number_of_cells",
            "dc_link_voltage_v",
            "switching_frequency_khz",
        ],

        "desired_information": [
            "semiconductor technology",
            "device voltage rating",
            "DC-link voltage",
            "number of stacked cells",
            "switching frequency",
            "device-count implications",
        ],
    },

    {
        "topic":
            "Efficiency and loss comparison",

        "priority_fields": [
            "rated_power_kw",
            "dc_link_voltage_v",
            "switching_frequency_khz",
            "efficiency_percent",
        ],

        "desired_information": [
            "measured efficiency",
            "output power",
            "DC-link voltage",
            "switching frequency",
            "semiconductor technology",
            "loss breakdown",
            "operating conditions",
        ],
    },

    {
        "topic":
            "Power density and thermal management",

        "priority_fields": [
            "rated_power_kw",
            "power_density_kw_per_l",
            "efficiency_percent",
        ],

        "desired_information": [
            "power density",
            "converter volume",
            "rated power",
            "cooling method",
            "thermal design",
            "measured efficiency",
        ],
    },

    {
        "topic":
            "Integrated modular motor drives",

        "priority_fields": [
            "rated_power_kw",
            "dc_link_voltage_v",
            "number_of_phases",
            "efficiency_percent",
            "power_density_kw_per_l",
        ],

        "desired_information": [
            "integrated inverter-machine architecture",
            "rated power",
            "DC-link voltage",
            "machine phase count",
            "cooling",
            "power density",
            "experimental maturity",
        ],
    },

    {
        "topic":
            "Experimental demonstrations",

        "priority_fields": [
            "rated_power_kw",
            "dc_link_voltage_v",
            "switching_frequency_khz",
            "efficiency_percent",
        ],

        "desired_information": [
            "hardware prototype",
            "rated power",
            "DC-link voltage",
            "switching frequency",
            "machine type",
            "experimental operating point",
            "efficiency",
        ],
    },
]


# =========================================================
# VALUE VALIDATION
# =========================================================

def has_numeric_value(value):
    """
    Return True only when the CSV entry contains a usable
    numerical value.
    """

    if value is None:
        return False

    text = str(
        value
    ).strip()

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

        float(
            text
        )

        return True

    except ValueError:

        return False


# =========================================================
# LOAD COMPARISON DATABASE
# =========================================================

def load_comparison_rows():

    if not COMPARISON_FILE.exists():

        raise FileNotFoundError(
            f"Could not find:\n"
            f"{COMPARISON_FILE}"
        )

    with COMPARISON_FILE.open(
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

    return rows


# =========================================================
# COUNT VERIFIED EVIDENCE PAPERS
# =========================================================

def count_evidence_papers():

    if not EVIDENCE_FILE.exists():

        return 0

    try:

        data = json.loads(
            EVIDENCE_FILE.read_text(
                encoding="utf-8"
            )
        )

    except json.JSONDecodeError:

        return 0

    count = 0

    for paper in data.get(
        "papers",
        []
    ):

        verified = any(

            claim.get(
                "verification_level"
            )
            == "FULL_TEXT_VERIFIED"

            for claim in paper.get(
                "claims",
                []
            )
        )

        if verified:

            count += 1

    return count


# =========================================================
# FIELD COVERAGE
# =========================================================

def analyze_fields(rows):

    results = []

    for (
        field,
        configuration,
    ) in NUMERICAL_TARGETS.items():

        count = sum(

            1

            for row in rows

            if has_numeric_value(
                row.get(
                    field
                )
            )
        )

        minimum = (
            configuration[
                "minimum"
            ]
        )

        missing = max(
            minimum - count,
            0,
        )

        if count == 0:

            priority = "CRITICAL"

        elif count < minimum:

            priority = "HIGH"

        else:

            priority = "SUFFICIENT"

        results.append(
            {
                "field":
                    field,

                "description":
                    configuration[
                        "description"
                    ],

                "valid_records":
                    count,

                "target_records":
                    minimum,

                "additional_records_needed":
                    missing,

                "priority":
                    priority,
            }
        )

    return results


# =========================================================
# PAIR COVERAGE
# =========================================================

def analyze_pairs(rows):

    results = []

    for pair in PAIR_TARGETS:

        x_column = (
            pair[
                "x"
            ]
        )

        y_column = (
            pair[
                "y"
            ]
        )

        count = sum(

            1

            for row in rows

            if (
                has_numeric_value(
                    row.get(
                        x_column
                    )
                )
                and
                has_numeric_value(
                    row.get(
                        y_column
                    )
                )
            )
        )

        minimum = pair[
            "minimum"
        ]

        missing = max(
            minimum - count,
            0,
        )

        if count == 0:

            priority = "CRITICAL"

        elif count < 3:

            priority = "HIGH"

        elif count < minimum:

            priority = "MEDIUM"

        else:

            priority = "SUFFICIENT"

        results.append(
            {
                "name":
                    pair[
                        "name"
                    ],

                "x_column":
                    x_column,

                "y_column":
                    y_column,

                "purpose":
                    pair[
                        "purpose"
                    ],

                "paired_records":
                    count,

                "target_records":
                    minimum,

                "additional_records_needed":
                    missing,

                "priority":
                    priority,
            }
        )

    return results


# =========================================================
# TOPIC PRIORITY
# =========================================================

def analyze_topics(
    field_results
):

    field_lookup = {

        item["field"]:
            item

        for item in field_results
    }

    results = []

    for topic in REVIEW_TOPICS:

        missing_fields = []

        score = 0

        for field in topic[
            "priority_fields"
        ]:

            result = field_lookup.get(
                field
            )

            if result is None:

                continue

            if (
                result["priority"]
                != "SUFFICIENT"
            ):

                missing_fields.append(
                    field
                )

            if (
                result["priority"]
                == "CRITICAL"
            ):

                score += 3

            elif (
                result["priority"]
                == "HIGH"
            ):

                score += 2

        if score >= 6:

            priority = "CRITICAL"

        elif score >= 3:

            priority = "HIGH"

        elif score > 0:

            priority = "MEDIUM"

        else:

            priority = "LOW"

        results.append(
            {
                "topic":
                    topic[
                        "topic"
                    ],

                "priority":
                    priority,

                "missing_fields":
                    missing_fields,

                "desired_information":
                    topic[
                        "desired_information"
                    ],
            }
        )

    priority_order = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3,
    }

    results.sort(
        key=lambda item:
            priority_order[
                item["priority"]
            ]
    )

    return results


# =========================================================
# CREATE SEARCH OBJECTIVES
# =========================================================

def create_search_objectives(
    topic_results
):

    objectives = []

    for index, topic in enumerate(
        topic_results,
        start=1,
    ):

        if (
            topic[
                "priority"
            ]
            == "LOW"
        ):

            continue

        desired = topic[
            "desired_information"
        ]

        search_focus = ", ".join(
            desired
        )

        objectives.append(
            {
                "priority_number":
                    index,

                "topic":
                    topic[
                        "topic"
                    ],

                "priority":
                    topic[
                        "priority"
                    ],

                "missing_fields":
                    topic[
                        "missing_fields"
                    ],

                "search_instruction":
                    (
                        "Find peer-reviewed papers "
                        "with experimental or quantitative "
                        "results concerning "
                        f"{topic['topic']}. "
                        "Prioritize publications reporting: "
                        f"{search_focus}."
                    ),
            }
        )

    return objectives


# =========================================================
# WRITE MARKDOWN REPORT
# =========================================================

def write_report(
    total_records,
    evidence_papers,
    fields,
    pairs,
    topics,
    search_objectives,
):

    lines = []

    lines.append(
        "# Targeted Literature Requirements"
    )

    lines.append("")

    lines.append(
        "This report identifies scientific information "
        "currently missing from the verified review "
        "database."
    )

    lines.append("")

    lines.append(
        f"- Comparison records: {total_records}"
    )

    lines.append(
        f"- Papers with full-text verified evidence: "
        f"{evidence_papers}"
    )

    lines.append("")

    # -----------------------------------------------------
    # FIELD COVERAGE
    # -----------------------------------------------------

    lines.append(
        "## 1. Numerical Data Requirements"
    )

    lines.append("")

    lines.append(
        "| Field | Valid | Target | Need | Priority |"
    )

    lines.append(
        "|---|---:|---:|---:|---|"
    )

    for item in fields:

        lines.append(
            f"| `{item['field']}` "
            f"| {item['valid_records']} "
            f"| {item['target_records']} "
            f"| {item['additional_records_needed']} "
            f"| {item['priority']} |"
        )

    lines.append("")

    # -----------------------------------------------------
    # FIGURE PAIRS
    # -----------------------------------------------------

    lines.append(
        "## 2. Quantitative Comparison Requirements"
    )

    lines.append("")

    for item in pairs:

        lines.append(
            f"### {item['name']}"
        )

        lines.append("")

        lines.append(
            f"- X: `{item['x_column']}`"
        )

        lines.append(
            f"- Y: `{item['y_column']}`"
        )

        lines.append(
            f"- Current paired records: "
            f"{item['paired_records']}"
        )

        lines.append(
            f"- Target paired records: "
            f"{item['target_records']}"
        )

        lines.append(
            f"- Additional records needed: "
            f"{item['additional_records_needed']}"
        )

        lines.append(
            f"- Priority: "
            f"**{item['priority']}**"
        )

        lines.append(
            f"- Scientific purpose: "
            f"{item['purpose']}"
        )

        lines.append("")

    # -----------------------------------------------------
    # TOPICS
    # -----------------------------------------------------

    lines.append(
        "## 3. Priority Review Topics"
    )

    lines.append("")

    for topic in topics:

        lines.append(
            f"### {topic['priority']} — "
            f"{topic['topic']}"
        )

        lines.append("")

        if topic[
            "missing_fields"
        ]:

            lines.append(
                "Missing quantitative fields:"
            )

            lines.append("")

            for field in topic[
                "missing_fields"
            ]:

                lines.append(
                    f"- `{field}`"
                )

        else:

            lines.append(
                "Current core quantitative coverage "
                "is sufficient."
            )

        lines.append("")

        lines.append(
            "Useful information to collect:"
        )

        lines.append("")

        for item in topic[
            "desired_information"
        ]:

            lines.append(
                f"- {item}"
            )

        lines.append("")

    # -----------------------------------------------------
    # SEARCH OBJECTIVES
    # -----------------------------------------------------

    lines.append(
        "## 4. Recommended Literature Searches"
    )

    lines.append("")

    if not search_objectives:

        lines.append(
            "Current coverage meets the configured "
            "minimum targets."
        )

    else:

        for objective in search_objectives:

            lines.append(
                f"### Search {objective['priority_number']}: "
                f"{objective['topic']}"
            )

            lines.append("")

            lines.append(
                f"Priority: "
                f"**{objective['priority']}**"
            )

            lines.append("")

            lines.append(
                objective[
                    "search_instruction"
                ]
            )

            lines.append("")

    REPORT_FILE.write_text(
        "\n".join(
            lines
        ),
        encoding="utf-8",
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print(
        "========================================"
    )

    print(
        "BUILDING TARGETED LITERATURE REQUIREMENTS"
    )

    print(
        "========================================"
    )

    print()

    # -----------------------------------------------------
    # LOAD DATA
    # -----------------------------------------------------

    try:

        rows = (
            load_comparison_rows()
        )

    except FileNotFoundError as error:

        print(error)

        print()

        print(
            "Run:"
        )

        print()

        print(
            "python build_comparison.py"
        )

        return

    evidence_papers = (
        count_evidence_papers()
    )

    # -----------------------------------------------------
    # ANALYZE
    # -----------------------------------------------------

    field_results = (
        analyze_fields(
            rows
        )
    )

    pair_results = (
        analyze_pairs(
            rows
        )
    )

    topic_results = (
        analyze_topics(
            field_results
        )
    )

    search_objectives = (
        create_search_objectives(
            topic_results
        )
    )

    # -----------------------------------------------------
    # CREATE DATABASE
    # -----------------------------------------------------

    database = {

        "comparison_records":
            len(rows),

        "full_text_verified_papers":
            evidence_papers,

        "field_requirements":
            field_results,

        "pair_requirements":
            pair_results,

        "topic_priorities":
            topic_results,

        "search_objectives":
            search_objectives,
    }

    # -----------------------------------------------------
    # SAVE JSON
    # -----------------------------------------------------

    JSON_OUTPUT_FILE.write_text(
        json.dumps(
            database,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # SAVE REPORT
    # -----------------------------------------------------

    write_report(
        len(rows),
        evidence_papers,
        field_results,
        pair_results,
        topic_results,
        search_objectives,
    )

    # -----------------------------------------------------
    # TERMINAL SUMMARY
    # -----------------------------------------------------

    print(
        f"Comparison records: "
        f"{len(rows)}"
    )

    print(
        f"Full-text verified papers: "
        f"{evidence_papers}"
    )

    print()

    print(
        "PRIORITY SEARCH TOPICS"
    )

    print(
        "----------------------------------------"
    )

    for topic in topic_results:

        if (
            topic["priority"]
            == "LOW"
        ):

            continue

        print(
            f"{topic['priority']:10} "
            f"{topic['topic']}"
        )

    print()

    print(
        "Files created:"
    )

    print()

    print(
        JSON_OUTPUT_FILE
    )

    print(
        REPORT_FILE
    )

    print()

    print(
        "========================================"
    )

    print(
        "LITERATURE TARGET ANALYSIS COMPLETE"
    )

    print(
        "========================================"
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()