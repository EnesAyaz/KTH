import json
import re
from pathlib import Path


# =========================================================
# PROJECT PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

DATA_DIR = ROOT_DIR / "data"

OUTPUT_DIR = ROOT_DIR / "output"

CANDIDATE_FILE = (
    DATA_DIR
    / "quantitative_candidate_papers.json"
)

TARGET_FILE = (
    DATA_DIR
    / "quantitative_literature_targets.json"
)

OUTPUT_JSON = (
    DATA_DIR
    / "quantitative_candidate_triage.json"
)

OUTPUT_MD = (
    OUTPUT_DIR
    / "quantitative_candidate_triage.md"
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
# PRIORITY WEIGHTS
# =========================================================

PRIORITY_BASE_WEIGHT = {
    "CRITICAL": 6,
    "HIGH": 4,
    "MEDIUM": 2,
    "LOW": 1,
}


EXPERIMENTAL_BONUS = {
    "HIGH": 8,
    "MEDIUM": 4,
    "LOW": 1,
    "UNKNOWN": 0,
}


QUANTITATIVE_BONUS = {
    "HIGH": 8,
    "MEDIUM": 4,
    "LOW": 1,
    "UNKNOWN": 0,
}


ACCESS_BONUS = {
    "HIGH": 4,
    "MEDIUM": 2,
    "LOW": 0,
    "UNKNOWN": 0,
}


TOPIC_BONUS = {
    # Direct SPB
    "Q01": 7,

    # GaN integrated modular motor drives
    "Q02": 5,

    # SiC integrated motor drives
    "Q03": 3,

    # High-power multiphase traction
    "Q04": 3,

    # High-voltage modular architecture
    "Q05": 5,
}


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
# NORMALIZATION
# =========================================================

def normalize_doi(
    doi,
):

    if not doi:

        return ""

    text = str(
        doi
    ).strip().lower()

    prefixes = [
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
    ]

    for prefix in prefixes:

        if text.startswith(
            prefix
        ):

            text = text[
                len(prefix):
            ]

    return text.strip()


def normalize_title(
    title,
):

    if not title:

        return ""

    text = str(
        title
    ).lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# =========================================================
# FIELD WEIGHT DATABASE
# =========================================================

def build_field_weights(
    targets,
):

    weights = {}

    for gap in targets.get(
        "field_gaps",
        []
    ):

        field = gap.get(
            "field"
        )

        if not field:

            continue

        needed = gap.get(
            "additional_records_needed",
            0,
        )

        priority = gap.get(
            "priority",
            "LOW",
        )

        # If the target is already met, do not reward
        # candidates for this field.
        if needed <= 0:

            weight = 0

        else:

            base = (
                PRIORITY_BASE_WEIGHT.get(
                    priority,
                    1,
                )
            )

            shortage_bonus = min(
                int(
                    needed
                ),
                5,
            )

            weight = (
                base
                + shortage_bonus
            )

        weights[
            field
        ] = {
            "weight":
                weight,

            "priority":
                priority,

            "additional_needed":
                needed,
        }

    return weights


# =========================================================
# PAIR WEIGHT DATABASE
# =========================================================

def build_pair_weights(
    targets,
):

    weights = {}

    for gap in targets.get(
        "pair_gaps",
        []
    ):

        name = gap.get(
            "name"
        )

        if not name:

            continue

        needed = gap.get(
            "additional_paired_records_needed",
            0,
        )

        priority = gap.get(
            "priority",
            "LOW",
        )

        if needed <= 0:

            weight = 0

        else:

            base = (
                PRIORITY_BASE_WEIGHT.get(
                    priority,
                    1,
                )
            )

            # Pair coverage is more valuable than
            # individual-field coverage because a figure
            # requires both values from the same system.
            shortage_bonus = (
                2
                * min(
                    int(
                        needed
                    ),
                    5,
                )
            )

            weight = (
                base
                + shortage_bonus
            )

        weights[
            name
        ] = {
            "weight":
                weight,

            "priority":
                priority,

            "additional_needed":
                needed,

            "x_column":
                gap.get(
                    "x_column"
                ),

            "y_column":
                gap.get(
                    "y_column"
                ),
        }

    return weights


# =========================================================
# ARCHITECTURE CATEGORY
# =========================================================

def classify_candidate(
    candidate,
):

    topics = set(
        candidate.get(
            "matched_topic_ids",
            []
        )
        or []
    )

    title = normalize_title(
        candidate.get(
            "title"
        )
    )

    if (
        "Q01" in topics
        or
        "stacked polyphase" in title
    ):

        return "DIRECT_SPB"

    if "Q02" in topics:

        return "GAN_INTEGRATED_DRIVE"

    if "Q03" in topics:

        return "SIC_INTEGRATED_DRIVE"

    if "Q04" in topics:

        return "MULTIPHASE_TRACTION"

    if "Q05" in topics:

        return "MODULAR_HIGH_VOLTAGE"

    return "OTHER"


# =========================================================
# SCORE ONE CANDIDATE
# =========================================================

def score_candidate(
    candidate,
    field_weights,
    pair_weights,
):

    score = 0

    score_breakdown = []

    expected_fields = set(
        candidate.get(
            "expected_quantitative_fields",
            []
        )
        or []
    )

    expected_pairs = set(
        candidate.get(
            "expected_quantitative_pairs",
            []
        )
        or []
    )

    # -----------------------------------------------------
    # FIELD SCORE
    # -----------------------------------------------------

    field_score = 0

    for field in sorted(
        expected_fields
    ):

        specification = (
            field_weights.get(
                field
            )
        )

        if not specification:

            continue

        weight = (
            specification[
                "weight"
            ]
        )

        if weight <= 0:

            continue

        field_score += (
            weight
        )

        score_breakdown.append(
            {
                "type":
                    "FIELD",

                "name":
                    field,

                "points":
                    weight,
            }
        )

    score += (
        field_score
    )

    # -----------------------------------------------------
    # PAIR SCORE
    # -----------------------------------------------------

    pair_score = 0

    matched_pairs = []

    for (
        pair_name,
        specification,
    ) in pair_weights.items():

        weight = (
            specification[
                "weight"
            ]
        )

        if weight <= 0:

            continue

        x_column = (
            specification.get(
                "x_column"
            )
        )

        y_column = (
            specification.get(
                "y_column"
            )
        )

        # Accept pair potential either when the agent
        # explicitly identified the pair OR when both
        # required fields are expected from the candidate.
        explicit_match = (
            pair_name
            in expected_pairs
        )

        inferred_field_match = (
            x_column
            in expected_fields
            and
            y_column
            in expected_fields
        )

        if (
            explicit_match
            or inferred_field_match
        ):

            pair_score += (
                weight
            )

            matched_pairs.append(
                pair_name
            )

            score_breakdown.append(
                {
                    "type":
                        "PAIR",

                    "name":
                        pair_name,

                    "points":
                        weight,
                }
            )

    score += (
        pair_score
    )

    # -----------------------------------------------------
    # EXPERIMENTAL RELEVANCE
    # -----------------------------------------------------

    experimental_level = str(
        candidate.get(
            "experimental_relevance",
            "UNKNOWN",
        )
    ).upper()

    experimental_score = (
        EXPERIMENTAL_BONUS.get(
            experimental_level,
            0,
        )
    )

    score += (
        experimental_score
    )

    if experimental_score:

        score_breakdown.append(
            {
                "type":
                    "EXPERIMENTAL",

                "name":
                    experimental_level,

                "points":
                    experimental_score,
            }
        )

    # -----------------------------------------------------
    # QUANTITATIVE RELEVANCE
    # -----------------------------------------------------

    quantitative_level = str(
        candidate.get(
            "quantitative_relevance",
            "UNKNOWN",
        )
    ).upper()

    quantitative_score = (
        QUANTITATIVE_BONUS.get(
            quantitative_level,
            0,
        )
    )

    score += (
        quantitative_score
    )

    if quantitative_score:

        score_breakdown.append(
            {
                "type":
                    "QUANTITATIVE",

                "name":
                    quantitative_level,

                "points":
                    quantitative_score,
            }
        )

    # -----------------------------------------------------
    # FULL-TEXT ACCESS
    # -----------------------------------------------------

    access_level = str(
        candidate.get(
            "full_text_access_likelihood",
            "UNKNOWN",
        )
    ).upper()

    access_score = (
        ACCESS_BONUS.get(
            access_level,
            0,
        )
    )

    score += (
        access_score
    )

    if access_score:

        score_breakdown.append(
            {
                "type":
                    "ACCESS",

                "name":
                    access_level,

                "points":
                    access_score,
            }
        )

    # -----------------------------------------------------
    # SEARCH TOPIC BONUS
    # -----------------------------------------------------

    topic_score = 0

    matched_topics = []

    for topic_id in candidate.get(
        "matched_topic_ids",
        []
    ) or []:

        bonus = (
            TOPIC_BONUS.get(
                topic_id,
                0,
            )
        )

        if bonus:

            topic_score += (
                bonus
            )

            matched_topics.append(
                topic_id
            )

    # Prevent candidates matching many broad search topics
    # from receiving an excessive topic bonus.
    topic_score = min(
        topic_score,
        10,
    )

    score += (
        topic_score
    )

    if topic_score:

        score_breakdown.append(
            {
                "type":
                    "TOPIC",

                "name":
                    ", ".join(
                        matched_topics
                    ),

                "points":
                    topic_score,
            }
        )

    # -----------------------------------------------------
    # DOI BONUS
    # -----------------------------------------------------

    doi = normalize_doi(
        candidate.get(
            "doi"
        )
    )

    doi_score = 0

    if doi:

        doi_score = 3

        score += (
            doi_score
        )

        score_breakdown.append(
            {
                "type":
                    "DOI",

                "name":
                    doi,

                "points":
                    doi_score,
            }
        )

    # -----------------------------------------------------
    # MULTI-FIELD BONUS
    # -----------------------------------------------------

    useful_field_count = sum(
        1
        for field in expected_fields
        if (
            field in field_weights
            and
            field_weights[
                field
            ][
                "weight"
            ]
            > 0
        )
    )

    multi_field_bonus = 0

    if useful_field_count >= 6:

        multi_field_bonus = 8

    elif useful_field_count >= 4:

        multi_field_bonus = 5

    elif useful_field_count >= 3:

        multi_field_bonus = 2

    score += (
        multi_field_bonus
    )

    if multi_field_bonus:

        score_breakdown.append(
            {
                "type":
                    "MULTI_FIELD",

                "name":
                    f"{useful_field_count} useful fields",

                "points":
                    multi_field_bonus,
            }
        )

    # -----------------------------------------------------
    # METADATA PENALTIES
    # -----------------------------------------------------

    penalty = 0

    if not candidate.get(
        "title"
    ):

        penalty += 20

    if not doi:

        penalty += 4

    if not candidate.get(
        "authors"
    ):

        penalty += 3

    if not candidate.get(
        "year"
    ):

        penalty += 3

    if penalty:

        score -= (
            penalty
        )

        score_breakdown.append(
            {
                "type":
                    "PENALTY",

                "name":
                    "Incomplete metadata",

                "points":
                    -penalty,
            }
        )

    return {
        "score":
            score,

        "field_score":
            field_score,

        "pair_score":
            pair_score,

        "experimental_score":
            experimental_score,

        "quantitative_score":
            quantitative_score,

        "access_score":
            access_score,

        "topic_score":
            topic_score,

        "doi_score":
            doi_score,

        "multi_field_bonus":
            multi_field_bonus,

        "penalty":
            penalty,

        "useful_field_count":
            useful_field_count,

        "matched_pairs":
            matched_pairs,

        "score_breakdown":
            score_breakdown,
    }


# =========================================================
# RECOMMENDATION
# =========================================================

def assign_recommendation(
    rank,
    total_candidates,
    score,
):

    # For a pool of approximately 10 candidates:
    #
    # Top 5 -> strongest download candidates
    # 6-8   -> useful reserve candidates
    # rest  -> hold unless they fill a special gap
    #
    # Score thresholds prevent a very weak candidate from
    # becoming "DOWNLOAD FIRST" simply because the pool is
    # small.

    if (
        rank <= 5
        and score >= 25
    ):

        return "DOWNLOAD FIRST"

    if (
        rank <= 8
        and score >= 15
    ):

        return "DOWNLOAD / RESERVE"

    return "HOLD"


# =========================================================
# BUILD TRIAGE
# =========================================================

def build_triage(
    candidates,
    field_weights,
    pair_weights,
):

    scored = []

    for candidate in candidates:

        result = score_candidate(
            candidate,
            field_weights,
            pair_weights,
        )

        scored.append(
            {
                **candidate,

                "architecture_category":
                    classify_candidate(
                        candidate
                    ),

                "score":
                    result[
                        "score"
                    ],

                "field_score":
                    result[
                        "field_score"
                    ],

                "pair_score":
                    result[
                        "pair_score"
                    ],

                "experimental_score":
                    result[
                        "experimental_score"
                    ],

                "quantitative_score":
                    result[
                        "quantitative_score"
                    ],

                "access_score":
                    result[
                        "access_score"
                    ],

                "topic_score":
                    result[
                        "topic_score"
                    ],

                "multi_field_bonus":
                    result[
                        "multi_field_bonus"
                    ],

                "metadata_penalty":
                    result[
                        "penalty"
                    ],

                "useful_field_count":
                    result[
                        "useful_field_count"
                    ],

                "matched_quantitative_pairs":
                    result[
                        "matched_pairs"
                    ],

                "score_breakdown":
                    result[
                        "score_breakdown"
                    ],
            }
        )

    # Highest score first.
    #
    # Tie-breaking:
    # 1. More pair value
    # 2. More useful fields
    # 3. Experimental relevance
    # 4. Title
    scored.sort(
        key=lambda item: (
            -item[
                "score"
            ],
            -item[
                "pair_score"
            ],
            -item[
                "useful_field_count"
            ],
            -item[
                "experimental_score"
            ],
            normalize_title(
                item.get(
                    "title"
                )
            ),
        )
    )

    total = len(
        scored
    )

    for rank, candidate in enumerate(
        scored,
        start=1,
    ):

        candidate[
            "rank"
        ] = rank

        candidate[
            "recommendation"
        ] = assign_recommendation(
            rank,
            total,
            candidate[
                "score"
            ],
        )

    return scored


# =========================================================
# MARKDOWN REPORT
# =========================================================

def write_markdown(
    triage,
    field_weights,
    pair_weights,
):

    lines = []

    lines.append(
        "# Quantitative Candidate Triage"
    )

    lines.append("")

    lines.append(
        "This ranking estimates how useful each "
        "candidate may be for filling the current "
        "quantitative gaps."
    )

    lines.append("")

    lines.append(
        "**Important:** the score is not a measure of "
        "scientific quality and does not verify any "
        "technical value. All candidates remain "
        "`CANDIDATE_METADATA_ONLY` until their PDFs are "
        "processed by the full-text Evidence Extractor."
    )

    lines.append("")

    # -----------------------------------------------------
    # SUMMARY TABLE
    # -----------------------------------------------------

    lines.append(
        "## Ranking"
    )

    lines.append("")

    lines.append(
        "| Rank | Score | Recommendation | Category | "
        "Useful Fields | Pair Matches | Paper |"
    )

    lines.append(
        "|---:|---:|---|---|---:|---:|---|"
    )

    for item in triage:

        title = str(
            item.get(
                "title",
                ""
            )
        ).replace(
            "|",
            "\\|"
        )

        lines.append(
            f"| {item['rank']} "
            f"| {item['score']} "
            f"| {item['recommendation']} "
            f"| {item['architecture_category']} "
            f"| {item['useful_field_count']} "
            f"| {len(item['matched_quantitative_pairs'])} "
            f"| {title} |"
        )

    lines.append("")

    # -----------------------------------------------------
    # DETAILS
    # -----------------------------------------------------

    lines.append(
        "## Candidate Details"
    )

    lines.append("")

    for item in triage:

        lines.append(
            f"### {item['rank']}. "
            f"{item.get('title')}"
        )

        lines.append("")

        lines.append(
            f"- Score: **{item['score']}**"
        )

        lines.append(
            f"- Recommendation: "
            f"**{item['recommendation']}**"
        )

        lines.append(
            f"- Architecture category: "
            f"`{item['architecture_category']}`"
        )

        lines.append(
            f"- DOI: "
            f"{item.get('doi')}"
        )

        lines.append(
            f"- Year: "
            f"{item.get('year')}"
        )

        lines.append(
            f"- Experimental relevance: "
            f"{item.get('experimental_relevance')}"
        )

        lines.append(
            f"- Quantitative relevance: "
            f"{item.get('quantitative_relevance')}"
        )

        lines.append(
            f"- Full-text access likelihood: "
            f"{item.get('full_text_access_likelihood')}"
        )

        lines.append(
            f"- Useful missing fields: "
            f"{item['useful_field_count']}"
        )

        lines.append("")

        lines.append(
            "Expected useful fields:"
        )

        lines.append("")

        fields = (
            item.get(
                "expected_quantitative_fields",
                []
            )
            or []
        )

        if fields:

            for field in fields:

                lines.append(
                    f"- `{field}`"
                )

        else:

            lines.append(
                "- None"
            )

        lines.append("")

        lines.append(
            "Matched figure pairs:"
        )

        lines.append("")

        pairs = (
            item[
                "matched_quantitative_pairs"
            ]
        )

        if pairs:

            for pair in pairs:

                lines.append(
                    f"- {pair}"
                )

        else:

            lines.append(
                "- None"
            )

        lines.append("")

        lines.append(
            "Score components:"
        )

        lines.append("")

        for component in item[
            "score_breakdown"
        ]:

            points = (
                component[
                    "points"
                ]
            )

            if points >= 0:

                points_text = (
                    f"+{points}"
                )

            else:

                points_text = str(
                    points
                )

            lines.append(
                f"- {component['type']}: "
                f"{component['name']} "
                f"({points_text})"
            )

        lines.append("")

        rationale = item.get(
            "selection_rationale"
        )

        if rationale:

            lines.append(
                "Discovery-stage rationale:"
            )

            lines.append("")

            lines.append(
                rationale
            )

            lines.append("")

    # -----------------------------------------------------
    # FIELD WEIGHTS
    # -----------------------------------------------------

    lines.append(
        "## Current Field Weights"
    )

    lines.append("")

    lines.append(
        "| Field | Weight | Additional Records Needed |"
    )

    lines.append(
        "|---|---:|---:|"
    )

    for (
        field,
        specification,
    ) in sorted(
        field_weights.items(),
        key=lambda pair: (
            -pair[1][
                "weight"
            ],
            pair[0],
        ),
    ):

        lines.append(
            f"| `{field}` "
            f"| {specification['weight']} "
            f"| {specification['additional_needed']} |"
        )

    lines.append("")

    # -----------------------------------------------------
    # PAIR WEIGHTS
    # -----------------------------------------------------

    lines.append(
        "## Current Pair Weights"
    )

    lines.append("")

    lines.append(
        "| Relationship | Weight | Additional Pairs Needed |"
    )

    lines.append(
        "|---|---:|---:|"
    )

    for (
        name,
        specification,
    ) in sorted(
        pair_weights.items(),
        key=lambda pair: (
            -pair[1][
                "weight"
            ],
            pair[0],
        ),
    ):

        lines.append(
            f"| {name} "
            f"| {specification['weight']} "
            f"| {specification['additional_needed']} |"
        )

    lines.append("")

    # -----------------------------------------------------
    # SELECTION NOTE
    # -----------------------------------------------------

    lines.append(
        "## Selection Note"
    )

    lines.append("")

    lines.append(
        "The next step should select approximately "
        "5-8 papers while maintaining architectural "
        "diversity. Do not automatically download every "
        "high-scoring paper if several candidates describe "
        "essentially the same system or research group."
    )

    lines.append("")

    OUTPUT_MD.write_text(
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
        "QUANTITATIVE CANDIDATE TRIAGE"
    )

    print(
        "========================================"
    )

    print()

    # -----------------------------------------------------
    # CHECK INPUTS
    # -----------------------------------------------------

    if not CANDIDATE_FILE.exists():

        print(
            "ERROR:"
        )

        print(
            "Could not find:"
        )

        print(
            CANDIDATE_FILE
        )

        print()

        print(
            "Run first:"
        )

        print()

        print(
            "python run_quantitative_literature_search.py"
        )

        return

    if not TARGET_FILE.exists():

        print(
            "ERROR:"
        )

        print(
            "Could not find:"
        )

        print(
            TARGET_FILE
        )

        return

    # -----------------------------------------------------
    # LOAD
    # -----------------------------------------------------

    candidate_database = load_json(
        CANDIDATE_FILE,
        {},
    )

    target_database = load_json(
        TARGET_FILE,
        {},
    )

    candidates = (
        candidate_database.get(
            "candidates",
            []
        )
    )

    if not candidates:

        print(
            "No quantitative candidates found."
        )

        return

    print(
        f"Candidate papers: "
        f"{len(candidates)}"
    )

    print()

    # -----------------------------------------------------
    # WEIGHTS
    # -----------------------------------------------------

    field_weights = (
        build_field_weights(
            target_database
        )
    )

    pair_weights = (
        build_pair_weights(
            target_database
        )
    )

    # -----------------------------------------------------
    # TRIAGE
    # -----------------------------------------------------

    triage = build_triage(
        candidates,
        field_weights,
        pair_weights,
    )

    # -----------------------------------------------------
    # SAVE JSON
    # -----------------------------------------------------

    output_database = {
        "candidate_count":
            len(
                triage
            ),

        "ranking_policy":
            (
                "Scores estimate potential usefulness "
                "for current quantitative evidence gaps. "
                "They do not verify scientific claims."
            ),

        "field_weights":
            field_weights,

        "pair_weights":
            pair_weights,

        "candidates":
            triage,
    }

    OUTPUT_JSON.write_text(
        json.dumps(
            output_database,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # MARKDOWN
    # -----------------------------------------------------

    write_markdown(
        triage,
        field_weights,
        pair_weights,
    )

    # -----------------------------------------------------
    # TERMINAL OUTPUT
    # -----------------------------------------------------

    print(
        "RANKED CANDIDATES"
    )

    print(
        "----------------------------------------"
    )

    for item in triage:

        print(
            f"{item['rank']:2d}. "
            f"Score {item['score']:3d} | "
            f"{item['recommendation']}"
        )

        print(
            f"    "
            f"{item.get('title')}"
        )

        print(
            f"    Category: "
            f"{item['architecture_category']}"
        )

        print(
            f"    Useful fields: "
            f"{item['useful_field_count']}"
        )

        print(
            f"    Useful pairs: "
            f"{len(item['matched_quantitative_pairs'])}"
        )

        print(
            f"    DOI: "
            f"{item.get('doi')}"
        )

        print()

    print(
        "========================================"
    )

    print(
        "SUMMARY"
    )

    print(
        "========================================"
    )

    print()

    download_first = sum(
        1
        for item in triage
        if (
            item[
                "recommendation"
            ]
            == "DOWNLOAD FIRST"
        )
    )

    reserve = sum(
        1
        for item in triage
        if (
            item[
                "recommendation"
            ]
            == "DOWNLOAD / RESERVE"
        )
    )

    hold = sum(
        1
        for item in triage
        if (
            item[
                "recommendation"
            ]
            == "HOLD"
        )
    )

    print(
        f"DOWNLOAD FIRST:       "
        f"{download_first}"
    )

    print(
        f"DOWNLOAD / RESERVE:   "
        f"{reserve}"
    )

    print(
        f"HOLD:                 "
        f"{hold}"
    )

    print()

    print(
        "Files created:"
    )

    print(
        OUTPUT_JSON
    )

    print(
        OUTPUT_MD
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "Do not treat these scores as scientific "
        "quality scores."
    )

    print(
        "Do not download everything yet."
    )

    print(
        "We will inspect the ranked list and choose "
        "approximately 5-8 complementary papers."
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()