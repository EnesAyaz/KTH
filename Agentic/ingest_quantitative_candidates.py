import json
import re
import shutil
from pathlib import Path


# =========================================================
# PROJECT PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"
PAPERS_DIR = ROOT_DIR / "papers"

APPROVED_FILE = (
    DATA_DIR
    / "approved_quantitative_candidates.json"
)

PAPERS_DATABASE_FILE = (
    DATA_DIR
    / "papers.json"
)

BACKUP_FILE = (
    DATA_DIR
    / "papers_backup_before_quantitative_ingest.json"
)

DOWNLOADED_FILE = (
    DATA_DIR
    / "downloaded_quantitative_papers.json"
)

REPORT_FILE = (
    OUTPUT_DIR
    / "quantitative_ingest_report.md"
)


DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

PAPERS_DIR.mkdir(
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
# LOAD APPROVED PAPERS
# =========================================================

def load_approved_papers():

    if not APPROVED_FILE.exists():

        raise FileNotFoundError(
            f"Could not find:\n"
            f"{APPROVED_FILE}"
        )

    database = load_json(
        APPROVED_FILE,
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
            "approved_quantitative_candidates.json "
            "contains no approved papers."
        )

    return papers


# =========================================================
# LOAD PAPERS DATABASE
# =========================================================

def load_papers_database():

    if not PAPERS_DATABASE_FILE.exists():

        return {
            "search_topic":
                "Review paper literature database",

            "papers": [],
        }

    database = load_json(
        PAPERS_DATABASE_FILE,
        {},
    )

    # Support older list-style format.
    if isinstance(
        database,
        list,
    ):

        return {
            "search_topic":
                "Review paper literature database",

            "papers":
                database,
        }

    if not isinstance(
        database,
        dict,
    ):

        return {
            "search_topic":
                "Review paper literature database",

            "papers": [],
        }

    if "papers" not in database:

        database[
            "papers"
        ] = []

    return database


# =========================================================
# EXISTING LOOKUPS
# =========================================================

def build_existing_lookups(
    papers,
):

    doi_lookup = {}
    title_lookup = {}
    key_lookup = {}

    for paper in papers:

        doi = normalize_doi(
            paper.get(
                "doi"
            )
        )

        title = normalize_title(
            paper.get(
                "title"
            )
        )

        citation_key = paper.get(
            "citation_key"
        )

        if doi:

            doi_lookup[
                doi
            ] = paper

        if title:

            title_lookup[
                title
            ] = paper

        if citation_key:

            key_lookup[
                citation_key
            ] = paper

    return (
        doi_lookup,
        title_lookup,
        key_lookup,
    )


# =========================================================
# FIND DUPLICATE
# =========================================================

def find_existing_paper(
    candidate,
    doi_lookup,
    title_lookup,
):

    doi = normalize_doi(
        candidate.get(
            "doi"
        )
    )

    title = normalize_title(
        candidate.get(
            "title"
        )
    )

    if (
        doi
        and doi in doi_lookup
    ):

        return (
            doi_lookup[
                doi
            ],
            "DOI match",
        )

    if (
        title
        and title in title_lookup
    ):

        return (
            title_lookup[
                title
            ],
            "Title match",
        )

    return (
        None,
        None,
    )


# =========================================================
# CONVERT CANDIDATE TO PAPERS.JSON RECORD
# =========================================================

def convert_candidate(
    candidate,
):
    """
    Convert discovery-stage candidate metadata into the
    papers.json structure.

    IMPORTANT:
    This function does not convert expected fields or the
    discovery rationale into scientific evidence.
    """

    matched_topics = (
        candidate.get(
            "matched_topic_ids",
            []
        )
        or []
    )

    expected_fields = (
        candidate.get(
            "expected_quantitative_fields",
            []
        )
        or []
    )

    return {
        "title":
            candidate.get(
                "title",
                ""
            ),

        "authors":
            candidate.get(
                "authors",
                []
            )
            or [],

        "year":
            candidate.get(
                "year"
            ),

        "doi":
            normalize_doi(
                candidate.get(
                    "doi"
                )
            ),

        "journal":
            candidate.get(
                "journal_or_venue"
            ),

        "citation_key":
            candidate.get(
                "citation_key"
            ),

        "main_contribution":
            (
                "Publication selected during the "
                "quantitative-gap literature search. "
                "Its technical contribution has not yet "
                "been verified from the full text."
            ),

        "relevant_sections":
            matched_topics,

        "quantitative_results":
            [],

        "limitations": [
            (
                "Full-text scientific evidence "
                "extraction is pending."
            ),
            (
                "Expected quantitative fields from the "
                "discovery stage must not be treated as "
                "verified values."
            ),
        ],

        "verification_status":
            "CANDIDATE_METADATA_ONLY",

        # Discovery metadata is retained separately.
        # The Writer must NOT treat these fields as
        # scientific evidence.
        "discovery_metadata": {
            "architecture_category":
                candidate.get(
                    "architecture_category"
                ),

            "expected_quantitative_fields":
                expected_fields,

            "expected_quantitative_pairs":
                candidate.get(
                    "expected_quantitative_pairs",
                    []
                )
                or [],

            "matched_quantitative_pairs":
                candidate.get(
                    "matched_quantitative_pairs",
                    []
                )
                or [],

            "experimental_relevance":
                candidate.get(
                    "experimental_relevance"
                ),

            "quantitative_relevance":
                candidate.get(
                    "quantitative_relevance"
                ),

            "selection_score":
                candidate.get(
                    "score"
                ),

            "original_rank":
                candidate.get(
                    "rank"
                ),
        },
    }


# =========================================================
# PDF CHECK
# =========================================================

def check_pdf(
    candidate,
):

    filename = candidate.get(
        "pdf_filename"
    )

    citation_key = candidate.get(
        "citation_key"
    )

    if not filename:

        filename = (
            f"{citation_key}.pdf"
        )

    path = (
        PAPERS_DIR
        / filename
    )

    return {
        "filename":
            filename,

        "path":
            path,

        "exists":
            path.exists(),
    }


# =========================================================
# BACKUP
# =========================================================

def create_backup():

    if not PAPERS_DATABASE_FILE.exists():
        return

    shutil.copy2(
        PAPERS_DATABASE_FILE,
        BACKUP_FILE,
    )


# =========================================================
# WRITE REPORT
# =========================================================

def write_report(
    results,
):

    lines = []

    lines.append(
        "# Quantitative Candidate Ingest Report"
    )

    lines.append("")

    lines.append(
        "This report records ingestion of the "
        "second-round quantitative literature candidates."
    )

    lines.append("")

    lines.append(
        "**Important:** papers listed here remain "
        "`CANDIDATE_METADATA_ONLY` until their PDFs are "
        "processed by the full-text Evidence Extractor."
    )

    lines.append("")

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    added = sum(
        1
        for item in results
        if item[
            "status"
        ] == "ADDED"
    )

    existing = sum(
        1
        for item in results
        if item[
            "status"
        ] == "ALREADY_PRESENT"
    )

    missing = sum(
        1
        for item in results
        if item[
            "status"
        ] == "MISSING_PDF"
    )

    conflicts = sum(
        1
        for item in results
        if item[
            "status"
        ] == "CITATION_KEY_CONFLICT"
    )

    lines.append(
        "## Summary"
    )

    lines.append("")

    lines.append(
        f"- Added: {added}"
    )

    lines.append(
        f"- Already present: {existing}"
    )

    lines.append(
        f"- Missing PDFs: {missing}"
    )

    lines.append(
        f"- Citation-key conflicts: {conflicts}"
    )

    lines.append("")

    # -----------------------------------------------------
    # TABLE
    # -----------------------------------------------------

    lines.append(
        "## Papers"
    )

    lines.append("")

    lines.append(
        "| Citation Key | Status | PDF | Title |"
    )

    lines.append(
        "|---|---|---|---|"
    )

    for item in results:

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
            f"| `{item.get('citation_key')}` "
            f"| {item.get('status')} "
            f"| `{item.get('pdf_filename')}` "
            f"| {title} |"
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
        "QUANTITATIVE PAPER INGEST"
    )

    print(
        "========================================"
    )

    print()

    # -----------------------------------------------------
    # LOAD
    # -----------------------------------------------------

    try:

        approved = (
            load_approved_papers()
        )

    except Exception as error:

        print(
            "ERROR:"
        )

        print(error)

        return

    database = (
        load_papers_database()
    )

    papers = database.get(
        "papers",
        []
    )

    # -----------------------------------------------------
    # BACKUP
    # -----------------------------------------------------

    create_backup()

    # -----------------------------------------------------
    # LOOKUPS
    # -----------------------------------------------------

    (
        doi_lookup,
        title_lookup,
        key_lookup,
    ) = build_existing_lookups(
        papers
    )

    # -----------------------------------------------------
    # PROCESS
    # -----------------------------------------------------

    results = []

    downloaded_records = []

    for candidate in approved:

        citation_key = candidate.get(
            "citation_key"
        )

        title = candidate.get(
            "title",
            ""
        )

        print(
            "----------------------------------------"
        )

        print(
            citation_key
        )

        print(
            title
        )

        # -------------------------------------------------
        # PDF
        # -------------------------------------------------

        pdf = check_pdf(
            candidate
        )

        if not pdf[
            "exists"
        ]:

            print(
                "PDF STATUS: MISSING"
            )

            print(
                pdf[
                    "path"
                ]
            )

            print()

            results.append(
                {
                    "citation_key":
                        citation_key,

                    "title":
                        title,

                    "pdf_filename":
                        pdf[
                            "filename"
                        ],

                    "status":
                        "MISSING_PDF",
                }
            )

            continue

        print(
            "PDF STATUS: FOUND"
        )

        # -------------------------------------------------
        # DUPLICATE DOI / TITLE
        # -------------------------------------------------

        existing, reason = (
            find_existing_paper(
                candidate,
                doi_lookup,
                title_lookup,
            )
        )

        if existing is not None:

            existing_key = (
                existing.get(
                    "citation_key"
                )
                or citation_key
            )

            print(
                "DATABASE STATUS: "
                "ALREADY PRESENT"
            )

            print(
                f"Existing key: "
                f"{existing_key}"
            )

            print()

            results.append(
                {
                    "citation_key":
                        existing_key,

                    "title":
                        title,

                    "pdf_filename":
                        pdf[
                            "filename"
                        ],

                    "status":
                        "ALREADY_PRESENT",

                    "reason":
                        reason,
                }
            )

            downloaded_records.append(
                {
                    "citation_key":
                        existing_key,

                    "title":
                        title,

                    "pdf_filename":
                        pdf[
                            "filename"
                        ],
                }
            )

            continue

        # -------------------------------------------------
        # KEY COLLISION
        # -------------------------------------------------

        if (
            citation_key
            in key_lookup
        ):

            print(
                "DATABASE STATUS: "
                "CITATION KEY CONFLICT"
            )

            print(
                "Conflicts with:"
            )

            print(
                key_lookup[
                    citation_key
                ].get(
                    "title"
                )
            )

            print()

            results.append(
                {
                    "citation_key":
                        citation_key,

                    "title":
                        title,

                    "pdf_filename":
                        pdf[
                            "filename"
                        ],

                    "status":
                        "CITATION_KEY_CONFLICT",
                }
            )

            continue

        # -------------------------------------------------
        # ADD
        # -------------------------------------------------

        record = convert_candidate(
            candidate
        )

        papers.append(
            record
        )

        normalized_doi = (
            normalize_doi(
                record.get(
                    "doi"
                )
            )
        )

        normalized_title = (
            normalize_title(
                record.get(
                    "title"
                )
            )
        )

        if normalized_doi:

            doi_lookup[
                normalized_doi
            ] = record

        if normalized_title:

            title_lookup[
                normalized_title
            ] = record

        key_lookup[
            citation_key
        ] = record

        downloaded_records.append(
            {
                "citation_key":
                    citation_key,

                "title":
                    title,

                "pdf_filename":
                    pdf[
                        "filename"
                    ],
            }
        )

        results.append(
            {
                "citation_key":
                    citation_key,

                "title":
                    title,

                "pdf_filename":
                    pdf[
                        "filename"
                    ],

                "status":
                    "ADDED",
            }
        )

        print(
            "DATABASE STATUS: ADDED"
        )

        print()

    # -----------------------------------------------------
    # SAVE PAPERS.JSON
    # -----------------------------------------------------

    database[
        "papers"
    ] = papers

    PAPERS_DATABASE_FILE.write_text(
        json.dumps(
            database,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # SAVE EXTRACTION MANIFEST
    # -----------------------------------------------------

    extraction_manifest = {
        "purpose":
            (
                "Second-round quantitative papers "
                "available for full-text evidence "
                "extraction."
            ),

        "papers":
            downloaded_records,
    }

    DOWNLOADED_FILE.write_text(
        json.dumps(
            extraction_manifest,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # REPORT
    # -----------------------------------------------------

    write_report(
        results
    )

    # -----------------------------------------------------
    # COUNTS
    # -----------------------------------------------------

    added = sum(
        1
        for item in results
        if item[
            "status"
        ] == "ADDED"
    )

    existing = sum(
        1
        for item in results
        if item[
            "status"
        ] == "ALREADY_PRESENT"
    )

    missing = sum(
        1
        for item in results
        if item[
            "status"
        ] == "MISSING_PDF"
    )

    conflicts = sum(
        1
        for item in results
        if item[
            "status"
        ] == "CITATION_KEY_CONFLICT"
    )

    # -----------------------------------------------------
    # TERMINAL SUMMARY
    # -----------------------------------------------------

    print(
        "========================================"
    )

    print(
        "INGEST SUMMARY"
    )

    print(
        "========================================"
    )

    print()

    print(
        f"Added:                "
        f"{added}"
    )

    print(
        f"Already present:      "
        f"{existing}"
    )

    print(
        f"Missing PDFs:         "
        f"{missing}"
    )

    print(
        f"Citation conflicts:   "
        f"{conflicts}"
    )

    print()

    print(
        "Updated database:"
    )

    print(
        PAPERS_DATABASE_FILE
    )

    print()

    print(
        "Backup:"
    )

    print(
        BACKUP_FILE
    )

    print()

    print(
        "Second-round extraction manifest:"
    )

    print(
        DOWNLOADED_FILE
    )

    print()

    print(
        "Report:"
    )

    print(
        REPORT_FILE
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "evidence.json was NOT modified."
    )

    print(
        "These papers are still not "
        "FULL_TEXT_VERIFIED."
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()