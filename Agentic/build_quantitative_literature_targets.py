import json
from pathlib import Path

import pandas as pd


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

TARGET_JSON_FILE = (
    DATA_DIR
    / "quantitative_literature_targets.json"
)

TARGET_MD_FILE = (
    OUTPUT_DIR
    / "quantitative_literature_targets.md"
)


DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# TARGET FIELD DEFINITIONS
# =========================================================

FIELD_TARGETS = {
    "rated_power_kw": {
        "desired_records": 6,
        "priority": "HIGH",
        "reason": (
            "Required for comparing converter and "
            "motor-drive scale."
        ),
    },

    "dc_link_voltage_v": {
        "desired_records": 6,
        "priority": "HIGH",
        "reason": (
            "Required to compare system voltage level "
            "and traction-drive applicability."
        ),
    },

    "cell_voltage_v": {
        "desired_records": 6,
        "priority": "HIGH",
        "reason": (
            "Important for demonstrating voltage "
            "partitioning in stacked or modular "
            "architectures."
        ),
    },

    "number_of_cells": {
        "desired_records": 6,
        "priority": "MEDIUM",
        "reason": (
            "Useful for architectural scaling, but "
            "cell definitions must be semantically "
            "consistent across papers."
        ),
    },

    "number_of_phases": {
        "desired_records": 6,
        "priority": "MEDIUM",
        "reason": (
            "Useful for comparing multiphase and "
            "multi-three-phase machine architectures."
        ),
    },

    "semiconductor_voltage_rating_v": {
        "desired_records": 6,
        "priority": "CRITICAL",
        "reason": (
            "Required for evaluating the relationship "
            "between converter cell voltage and "
            "semiconductor device voltage class."
        ),
    },

    "semiconductor_current_rating_a": {
        "desired_records": 5,
        "priority": "MEDIUM",
        "reason": (
            "Useful for device utilization and "
            "semiconductor scaling comparisons."
        ),
    },

    "switching_frequency_khz": {
        "desired_records": 6,
        "priority": "CRITICAL",
        "reason": (
            "Required for switching-frequency versus "
            "device-technology and efficiency "
            "comparisons."
        ),
    },

    "efficiency_percent": {
        "desired_records": 6,
        "priority": "CRITICAL",
        "reason": (
            "Required for meaningful converter and "
            "drive efficiency comparison."
        ),
    },

    "power_density_kw_per_l": {
        "desired_records": 5,
        "priority": "CRITICAL",
        "reason": (
            "Required for evaluating the integration "
            "and packaging benefit of modular and "
            "integrated motor drives."
        ),
    },
}


# =========================================================
# PAIRED-FIELD TARGETS
# =========================================================

PAIR_TARGETS = [
    {
        "name":
            "Cell voltage vs semiconductor voltage rating",

        "x":
            "cell_voltage_v",

        "y":
            "semiconductor_voltage_rating_v",

        "desired_records":
            6,

        "priority":
            "CRITICAL",

        "scientific_purpose":
            (
                "Evaluate whether distributing the "
                "DC-link voltage across converter cells "
                "enables lower-voltage semiconductor "
                "devices."
            ),
    },

    {
        "name":
            (
                "Semiconductor voltage rating vs "
                "switching frequency"
            ),

        "x":
            "semiconductor_voltage_rating_v",

        "y":
            "switching_frequency_khz",

        "desired_records":
            6,

        "priority":
            "CRITICAL",

        "scientific_purpose":
            (
                "Evaluate the relationship between "
                "device voltage class and achievable "
                "switching frequency."
            ),
    },

    {
        "name":
            "Efficiency vs switching frequency",

        "x":
            "switching_frequency_khz",

        "y":
            "efficiency_percent",

        "desired_records":
            6,

        "priority":
            "CRITICAL",

        "scientific_purpose":
            (
                "Support a review-level comparison of "
                "switching-frequency and efficiency "
                "tradeoffs."
            ),
    },

    {
        "name":
            "Efficiency vs power density",

        "x":
            "power_density_kw_per_l",

        "y":
            "efficiency_percent",

        "desired_records":
            5,

        "priority":
            "CRITICAL",

        "scientific_purpose":
            (
                "Compare system integration and "
                "efficiency rather than treating power "
                "density and efficiency independently."
            ),
    },

    {
        "name":
            "Rated power vs DC-link voltage",

        "x":
            "rated_power_kw",

        "y":
            "dc_link_voltage_v",

        "desired_records":
            6,

        "priority":
            "HIGH",

        "scientific_purpose":
            (
                "Compare voltage and power scaling "
                "between laboratory demonstrators, "
                "integrated drives, and traction-scale "
                "systems."
            ),
    },
]


# =========================================================
# SEARCH TOPIC DEFINITIONS
# =========================================================

SEARCH_TOPICS = [
    {
        "topic_id":
            "Q01",

        "topic":
            (
                "Experimental stacked polyphase bridge "
                "converter implementations"
            ),

        "priority":
            "CRITICAL",

        "keywords": [
            "stacked polyphase bridge converter",
            "stacked polyphase bridges converter",
            "SPB converter",
            "multi-three-phase motor drive",
            "experimental",
            "prototype",
        ],

        "desired_fields": [
            "rated_power_kw",
            "dc_link_voltage_v",
            "cell_voltage_v",
            "number_of_cells",
            "number_of_phases",
            "semiconductor_voltage_rating_v",
            "switching_frequency_khz",
            "efficiency_percent",
        ],

        "selection_goal":
            (
                "Find direct SPB publications containing "
                "actual prototype specifications and "
                "quantitative converter data."
            ),
    },

    {
        "topic_id":
            "Q02",

        "topic":
            (
                "GaN integrated modular motor drives "
                "with quantitative performance"
            ),

        "priority":
            "CRITICAL",

        "keywords": [
            "GaN integrated motor drive",
            "GaN modular motor drive",
            "integrated modular motor drive",
            "power density",
            "efficiency",
            "switching frequency",
        ],

        "desired_fields": [
            "rated_power_kw",
            "dc_link_voltage_v",
            "semiconductor_voltage_rating_v",
            "switching_frequency_khz",
            "efficiency_percent",
            "power_density_kw_per_l",
            "cooling_method",
        ],

        "selection_goal":
            (
                "Find experimentally validated GaN "
                "integrated-drive systems reporting both "
                "efficiency and power-density metrics."
            ),
    },

    {
        "topic_id":
            "Q03",

        "topic":
            (
                "SiC integrated motor drives with "
                "efficiency and power density"
            ),

        "priority":
            "HIGH",

        "keywords": [
            "SiC integrated motor drive",
            "SiC traction inverter",
            "integrated inverter motor",
            "power density",
            "efficiency",
            "experimental",
        ],

        "desired_fields": [
            "rated_power_kw",
            "dc_link_voltage_v",
            "semiconductor_voltage_rating_v",
            "switching_frequency_khz",
            "efficiency_percent",
            "power_density_kw_per_l",
            "cooling_method",
        ],

        "selection_goal":
            (
                "Provide a strong SiC benchmark against "
                "the GaN and stacked architectures."
            ),
    },

    {
        "topic_id":
            "Q04",

        "topic":
            (
                "Multiphase high-power traction inverter "
                "experimental demonstrations"
            ),

        "priority":
            "HIGH",

        "keywords": [
            "multiphase traction inverter",
            "six phase inverter electric vehicle",
            "nine phase motor drive inverter",
            "multi three phase traction",
            "SiC",
            "experimental",
        ],

        "desired_fields": [
            "rated_power_kw",
            "dc_link_voltage_v",
            "number_of_phases",
            "semiconductor_voltage_rating_v",
            "switching_frequency_khz",
            "efficiency_percent",
            "power_density_kw_per_l",
        ],

        "selection_goal":
            (
                "Provide high-power traction-scale "
                "benchmarks with comparable voltage, "
                "power, semiconductor, switching, and "
                "efficiency data."
            ),
    },

    {
        "topic_id":
            "Q05",

        "topic":
            (
                "High-voltage modular motor-drive "
                "architectures using lower-voltage "
                "semiconductor devices"
            ),

        "priority":
            "CRITICAL",

        "keywords": [
            "modular motor drive",
            "series connected inverter cells",
            "segmented inverter motor drive",
            "lower voltage semiconductor",
            "high voltage dc link",
            "multiphase",
        ],

        "desired_fields": [
            "dc_link_voltage_v",
            "cell_voltage_v",
            "number_of_cells",
            "number_of_phases",
            "semiconductor_voltage_rating_v",
            "switching_frequency_khz",
        ],

        "selection_goal":
            (
                "Strengthen the central SPB review "
                "argument concerning DC-link voltage "
                "partitioning and semiconductor voltage "
                "scaling."
            ),
    },
]


# =========================================================
# UTILITY FUNCTIONS
# =========================================================

def has_value(value):
    """
    Return True when a comparison-table cell contains a
    meaningful value.
    """

    if pd.isna(value):
        return False

    if isinstance(
        value,
        str,
    ):

        text = value.strip()

        if not text:
            return False

        if text.lower() in {
            "nan",
            "none",
            "null",
        }:

            return False

    return True


def count_available(
    dataframe,
    column,
):

    if column not in dataframe.columns:
        return 0

    return sum(
        1
        for value in dataframe[
            column
        ]
        if has_value(
            value
        )
    )


def count_pair(
    dataframe,
    x_column,
    y_column,
):

    if (
        x_column not in dataframe.columns
        or y_column not in dataframe.columns
    ):

        return 0

    count = 0

    for _, row in dataframe.iterrows():

        if (
            has_value(
                row[
                    x_column
                ]
            )
            and
            has_value(
                row[
                    y_column
                ]
            )
        ):

            count += 1

    return count


def priority_rank(
    priority,
):

    ranking = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    return ranking.get(
        priority,
        0,
    )


# =========================================================
# BUILD FIELD GAP REPORT
# =========================================================

def build_field_gaps(
    dataframe,
):

    gaps = []

    for (
        field,
        specification,
    ) in FIELD_TARGETS.items():

        available = count_available(
            dataframe,
            field,
        )

        desired = (
            specification[
                "desired_records"
            ]
        )

        missing = max(
            desired - available,
            0,
        )

        if available == 0:

            status = (
                "NO DATA"
            )

        elif available < desired:

            status = (
                "MORE DATA NEEDED"
            )

        else:

            status = (
                "TARGET MET"
            )

        gaps.append(
            {
                "field":
                    field,

                "available_records":
                    available,

                "desired_records":
                    desired,

                "additional_records_needed":
                    missing,

                "priority":
                    specification[
                        "priority"
                    ],

                "status":
                    status,

                "reason":
                    specification[
                        "reason"
                    ],
            }
        )

    gaps.sort(
        key=lambda item: (
            -priority_rank(
                item[
                    "priority"
                ]
            ),
            -item[
                "additional_records_needed"
            ],
        )
    )

    return gaps


# =========================================================
# BUILD PAIRED GAP REPORT
# =========================================================

def build_pair_gaps(
    dataframe,
):

    gaps = []

    for specification in PAIR_TARGETS:

        available = count_pair(
            dataframe,
            specification[
                "x"
            ],
            specification[
                "y"
            ],
        )

        desired = (
            specification[
                "desired_records"
            ]
        )

        missing = max(
            desired - available,
            0,
        )

        if available == 0:

            status = (
                "NO DATA"
            )

        elif available < desired:

            status = (
                "MORE DATA NEEDED"
            )

        else:

            status = (
                "TARGET MET"
            )

        gaps.append(
            {
                "name":
                    specification[
                        "name"
                    ],

                "x_column":
                    specification[
                        "x"
                    ],

                "y_column":
                    specification[
                        "y"
                    ],

                "available_paired_records":
                    available,

                "desired_paired_records":
                    desired,

                "additional_paired_records_needed":
                    missing,

                "priority":
                    specification[
                        "priority"
                    ],

                "status":
                    status,

                "scientific_purpose":
                    specification[
                        "scientific_purpose"
                    ],
            }
        )

    gaps.sort(
        key=lambda item: (
            -priority_rank(
                item[
                    "priority"
                ]
            ),
            -item[
                "additional_paired_records_needed"
            ],
        )
    )

    return gaps


# =========================================================
# EXISTING PAPER SUMMARY
# =========================================================

def build_existing_paper_summary(
    dataframe,
):

    records = []

    useful_columns = [
        "citation_key",
        "title",
        "topology",
        "rated_power_kw",
        "dc_link_voltage_v",
        "cell_voltage_v",
        "number_of_cells",
        "number_of_phases",
        "semiconductor_technology",
        "semiconductor_voltage_rating_v",
        "switching_frequency_khz",
        "efficiency_percent",
        "power_density_kw_per_l",
        "experimental_level",
    ]

    for _, row in dataframe.iterrows():

        record = {}

        for column in useful_columns:

            if column not in dataframe.columns:
                continue

            value = row[
                column
            ]

            if not has_value(
                value
            ):
                continue

            if hasattr(
                value,
                "item",
            ):

                try:
                    value = value.item()

                except Exception:
                    pass

            record[
                column
            ] = value

        records.append(
            record
        )

    return records


# =========================================================
# SEARCH REQUIREMENTS
# =========================================================

def build_search_requirements(
    field_gaps,
    pair_gaps,
):

    critical_fields = [

        gap[
            "field"
        ]

        for gap in field_gaps

        if (
            gap[
                "priority"
            ]
            == "CRITICAL"
            and
            gap[
                "additional_records_needed"
            ]
            > 0
        )
    ]

    high_fields = [

        gap[
            "field"
        ]

        for gap in field_gaps

        if (
            gap[
                "priority"
            ]
            == "HIGH"
            and
            gap[
                "additional_records_needed"
            ]
            > 0
        )
    ]

    critical_pairs = [

        {
            "name":
                gap[
                    "name"
                ],

            "x_column":
                gap[
                    "x_column"
                ],

            "y_column":
                gap[
                    "y_column"
                ],

            "additional_records_needed":
                gap[
                    "additional_paired_records_needed"
                ],
        }

        for gap in pair_gaps

        if (
            gap[
                "priority"
            ]
            == "CRITICAL"
            and
            gap[
                "additional_paired_records_needed"
            ]
            > 0
        )
    ]

    return {
        "desired_number_of_new_papers":
            {
                "minimum": 5,
                "preferred": 8,
                "maximum": 10,
            },

        "critical_missing_fields":
            critical_fields,

        "high_priority_missing_fields":
            high_fields,

        "critical_missing_pairs":
            critical_pairs,

        "paper_selection_rules": [
            (
                "Prefer peer-reviewed journal or major "
                "IEEE/IET/EPE conference publications."
            ),

            (
                "Prefer papers with an accessible full "
                "text that can later be downloaded and "
                "processed by the Evidence Extractor."
            ),

            (
                "Prefer experimental prototypes over "
                "purely conceptual papers."
            ),

            (
                "Prefer papers reporting several target "
                "quantitative fields in the same system."
            ),

            (
                "Do not select a paper solely because it "
                "mentions GaN, SiC, SPB, or integrated "
                "motor drives."
            ),

            (
                "Do not infer efficiency, power density, "
                "device rating, or switching frequency "
                "from metadata or titles."
            ),

            (
                "Do not treat simulation-only results as "
                "experimental measurements."
            ),

            (
                "Avoid duplicates of papers already "
                "present in the literature database."
            ),

            (
                "For number_of_cells, distinguish actual "
                "series SPB converter cells from generic "
                "motor-drive modules or segmented "
                "inverter units."
            ),
        ],

        "ideal_new_paper":
            (
                "An ideal candidate reports at least "
                "four of the following in one "
                "experimentally demonstrated system: "
                "rated power, DC-link voltage, cell "
                "voltage, semiconductor voltage rating, "
                "switching frequency, efficiency, and "
                "power density."
            ),
    }


# =========================================================
# WRITE MARKDOWN REPORT
# =========================================================

def write_markdown(
    dataframe,
    field_gaps,
    pair_gaps,
    search_requirements,
):

    lines = []

    lines.append(
        "# Quantitative Literature Targets"
    )

    lines.append("")

    lines.append(
        "This report converts the current comparison "
        "database coverage into explicit targets for "
        "the next literature-search round."
    )

    lines.append("")

    lines.append(
        f"Current comparison records: "
        f"{len(dataframe)}"
    )

    lines.append("")

    # -----------------------------------------------------
    # FIELD COVERAGE
    # -----------------------------------------------------

    lines.append(
        "## Individual Field Coverage"
    )

    lines.append("")

    lines.append(
        "| Field | Available | Target | Additional Needed | Priority | Status |"
    )

    lines.append(
        "|---|---:|---:|---:|---|---|"
    )

    for gap in field_gaps:

        lines.append(
            f"| `{gap['field']}` "
            f"| {gap['available_records']} "
            f"| {gap['desired_records']} "
            f"| {gap['additional_records_needed']} "
            f"| {gap['priority']} "
            f"| {gap['status']} |"
        )

    lines.append("")

    # -----------------------------------------------------
    # PAIRED COVERAGE
    # -----------------------------------------------------

    lines.append(
        "## Paired Quantitative Coverage"
    )

    lines.append("")

    lines.append(
        "| Figure Relationship | Current Pairs | Target | Additional Needed | Priority |"
    )

    lines.append(
        "|---|---:|---:|---:|---|"
    )

    for gap in pair_gaps:

        lines.append(
            f"| {gap['name']} "
            f"| {gap['available_paired_records']} "
            f"| {gap['desired_paired_records']} "
            f"| {gap['additional_paired_records_needed']} "
            f"| {gap['priority']} |"
        )

    lines.append("")

    # -----------------------------------------------------
    # PRIORITY SEARCH
    # -----------------------------------------------------

    lines.append(
        "## Priority Literature Search Topics"
    )

    lines.append("")

    for topic in SEARCH_TOPICS:

        lines.append(
            f"### {topic['topic_id']} — "
            f"{topic['topic']}"
        )

        lines.append("")

        lines.append(
            f"Priority: **{topic['priority']}**"
        )

        lines.append("")

        lines.append(
            "Desired fields:"
        )

        lines.append("")

        for field in topic[
            "desired_fields"
        ]:

            lines.append(
                f"- `{field}`"
            )

        lines.append("")

        lines.append(
            "Selection goal:"
        )

        lines.append("")

        lines.append(
            topic[
                "selection_goal"
            ]
        )

        lines.append("")

    # -----------------------------------------------------
    # IDEAL PAPER
    # -----------------------------------------------------

    lines.append(
        "## Ideal Candidate"
    )

    lines.append("")

    lines.append(
        search_requirements[
            "ideal_new_paper"
        ]
    )

    lines.append("")

    # -----------------------------------------------------
    # SEMANTIC WARNING
    # -----------------------------------------------------

    lines.append(
        "## Important Semantic Warning"
    )

    lines.append("")

    lines.append(
        "`number_of_cells` must not automatically "
        "combine SPB series cells, generic inverter "
        "modules, phase modules, and segmented drive "
        "units. These architectures must be classified "
        "before using the values in the same figure."
    )

    lines.append("")

    lines.append(
        "In particular, architecture counts from "
        "integrated modular motor-drive papers should "
        "not be interpreted as SPB series-cell counts "
        "unless the full text explicitly supports that "
        "interpretation."
    )

    lines.append("")

    TARGET_MD_FILE.write_text(
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
        "QUANTITATIVE LITERATURE TARGET BUILDER"
    )

    print(
        "========================================"
    )

    print()

    # -----------------------------------------------------
    # CHECK COMPARISON FILE
    # -----------------------------------------------------

    if not COMPARISON_FILE.exists():

        print(
            "ERROR:"
        )

        print(
            "Could not find:"
        )

        print(
            COMPARISON_FILE
        )

        print()

        print(
            "Run first:"
        )

        print()

        print(
            "python build_comparison.py"
        )

        return

    # -----------------------------------------------------
    # LOAD DATA
    # -----------------------------------------------------

    dataframe = pd.read_csv(
        COMPARISON_FILE
    )

    print(
        f"Comparison records: "
        f"{len(dataframe)}"
    )

    print()

    # -----------------------------------------------------
    # ANALYZE
    # -----------------------------------------------------

    field_gaps = (
        build_field_gaps(
            dataframe
        )
    )

    pair_gaps = (
        build_pair_gaps(
            dataframe
        )
    )

    existing_papers = (
        build_existing_paper_summary(
            dataframe
        )
    )

    search_requirements = (
        build_search_requirements(
            field_gaps,
            pair_gaps,
        )
    )

    # -----------------------------------------------------
    # OUTPUT DATABASE
    # -----------------------------------------------------

    database = {
        "purpose":
            (
                "Target the second literature-search "
                "round toward missing quantitative "
                "comparison data."
            ),

        "current_comparison_record_count":
            len(
                dataframe
            ),

        "field_gaps":
            field_gaps,

        "pair_gaps":
            pair_gaps,

        "search_requirements":
            search_requirements,

        "search_topics":
            SEARCH_TOPICS,

        "existing_comparison_records":
            existing_papers,

        "scientific_constraints": [
            (
                "Only full-text-verified values may "
                "enter comparison.csv."
            ),

            (
                "Metadata and abstracts may identify "
                "candidate papers but may not support "
                "quantitative comparison values."
            ),

            (
                "Do not estimate numerical values from "
                "figures."
            ),

            (
                "Do not infer missing values from "
                "engineering relationships."
            ),

            (
                "Operating conditions must be retained "
                "when comparing efficiency and power "
                "density."
            ),

            (
                "SPB cells must be distinguished from "
                "generic integrated motor-drive "
                "modules."
            ),
        ],
    }

    # -----------------------------------------------------
    # WRITE JSON
    # -----------------------------------------------------

    TARGET_JSON_FILE.write_text(
        json.dumps(
            database,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # WRITE MARKDOWN
    # -----------------------------------------------------

    write_markdown(
        dataframe,
        field_gaps,
        pair_gaps,
        search_requirements,
    )

    # -----------------------------------------------------
    # TERMINAL SUMMARY
    # -----------------------------------------------------

    print(
        "CRITICAL FIELD GAPS"
    )

    print(
        "----------------------------------------"
    )

    critical_gaps = [

        gap

        for gap in field_gaps

        if (
            gap[
                "priority"
            ]
            == "CRITICAL"
            and
            gap[
                "additional_records_needed"
            ]
            > 0
        )
    ]

    for gap in critical_gaps:

        print(
            f"{gap['field']}: "
            f"{gap['available_records']} / "
            f"{gap['desired_records']} "
            f"(need +"
            f"{gap['additional_records_needed']})"
        )

    print()

    print(
        "CRITICAL PAIRED GAPS"
    )

    print(
        "----------------------------------------"
    )

    critical_pairs = [

        gap

        for gap in pair_gaps

        if (
            gap[
                "priority"
            ]
            == "CRITICAL"
            and
            gap[
                "additional_paired_records_needed"
            ]
            > 0
        )
    ]

    for gap in critical_pairs:

        print(
            f"{gap['name']}: "
            f"{gap['available_paired_records']} / "
            f"{gap['desired_paired_records']} "
            f"(need +"
            f"{gap['additional_paired_records_needed']})"
        )

    print()

    print(
        "NEXT SEARCH TOPICS"
    )

    print(
        "----------------------------------------"
    )

    for topic in SEARCH_TOPICS:

        print(
            f"{topic['priority']:8s} "
            f"{topic['topic_id']} "
            f"{topic['topic']}"
        )

    print()

    print(
        "Files created:"
    )

    print(
        TARGET_JSON_FILE
    )

    print(
        TARGET_MD_FILE
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "This script does NOT search the internet."
    )

    print(
        "It only defines the quantitative evidence "
        "targets for the next literature agent."
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()