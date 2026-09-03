import json
import re
import shutil
from pathlib import Path


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

APPROVED_FILE = (
    DATA_DIR
    / "approved_candidates.json"
)

PAPERS_DATABASE_FILE = (
    DATA_DIR
    / "papers.json"
)

BACKUP_FILE = (
    DATA_DIR
    / "papers_backup_before_approved_merge.json"
)

MERGE_REPORT_FILE = (
    OUTPUT_DIR
    / "approved_papers_merge_report.md"
)

DOWNLOADED_DATABASE_FILE = (
    DATA_DIR
    / "downloaded_approved_papers.json"
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


# =========================================================
# NORMALIZATION
# =========================================================

def normalize_doi(doi):
    """
    Normalize DOI strings for duplicate comparison.
    """

    if not doi:
        return None

    text = str(
        doi
    ).strip().lower()

    prefixes = [
        "https://doi.org/",
        "http://doi.org/",
        "http://dx.doi.org/",
        "https://dx.doi.org/",
        "doi:",
    ]

    for prefix in prefixes:

        if text.startswith(prefix):

            text = text[
                len(prefix):
            ]

    return text.strip()


def normalize_title(title):
    """
    Normalize paper titles for duplicate detection.
    """

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
# LOAD APPROVED PAPERS
# =========================================================

def load_approved_papers():

    if not APPROVED_FILE.exists():

        raise FileNotFoundError(
            f"Could not find:\n"
            f"{APPROVED_FILE}"
        )

    data = load_json(
        APPROVED_FILE,
        {
            "papers": []
        },
    )

    return data.get(
        "papers",
        []
    )


# =========================================================
# LOAD CURRENT PAPERS DATABASE
# =========================================================

def load_papers_database():

    if not PAPERS_DATABASE_FILE.exists():

        return {
            "search_topic":
                "Review paper literature database",

            "papers": [],
        }

    data = load_json(
        PAPERS_DATABASE_FILE,
        {},
    )

    # Support old list-style format.
    if isinstance(
        data,
        list,
    ):

        return {
            "search_topic":
                "Review paper literature database",

            "papers":
                data,
        }

    if not isinstance(
        data,
        dict,
    ):

        return {
            "search_topic":
                "Review paper literature database",

            "papers": [],
        }

    if "papers" not in data:

        data["papers"] = []

    return data


# =========================================================
# BUILD DATABASE LOOKUPS
# =========================================================

def build_existing_lookups(
    papers,
):

    doi_lookup = {}

    title_lookup = {}

    citation_key_lookup = {}

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

        citation_key = (
            paper.get(
                "citation_key"
            )
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

            citation_key_lookup[
                citation_key
            ] = paper

    return (
        doi_lookup,
        title_lookup,
        citation_key_lookup,
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
# CONVERT APPROVED CANDIDATE
# TO PAPERS.JSON FORMAT
# =========================================================

def convert_candidate_to_paper_record(
    candidate,
):
    """
    Convert candidate metadata into the PaperRecord-style
    structure used by papers.json.

    IMPORTANT:
    No technical contribution is claimed to be verified.
    """

    target_topics = (
        candidate.get(
            "target_topics",
            []
        )
        or []
    )

    reason = (
        candidate.get(
            "reason_for_selection"
        )
        or
        (
            "Candidate selected for full-text "
            "scientific evidence extraction."
        )
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
                "Candidate publication selected for "
                "full-text evidence extraction. "
                "Technical contribution has not yet "
                "been full-text verified. "
                "Selection rationale: "
                + reason
            ),

        "relevant_sections":
            target_topics,

        "quantitative_results":
            [],

        "limitations":
            [
                (
                    "Technical claims and numerical "
                    "results have not yet been verified "
                    "from the full text."
                )
            ],

        "verification_status":
            "CANDIDATE_METADATA_ONLY",
    }


# =========================================================
# CHECK PDF
# =========================================================

def check_pdf(
    candidate,
):

    citation_key = (
        candidate.get(
            "citation_key"
        )
    )

    requested_filename = (
        candidate.get(
            "pdf_filename"
        )
    )

    # Normally approved_candidates.json already contains
    # the exact PDF filename.
    if not requested_filename:

        requested_filename = (
            f"{citation_key}.pdf"
        )

    requested_path = (
        PAPERS_DIR
        / requested_filename
    )

    if requested_path.exists():

        return {
            "found": True,
            "filename":
                requested_filename,
            "path":
                requested_path,
            "renamed": False,
        }

    # -----------------------------------------------------
    # SECONDARY CHECK:
    # citation_key.pdf
    # -----------------------------------------------------

    fallback_filename = (
        f"{citation_key}.pdf"
    )

    fallback_path = (
        PAPERS_DIR
        / fallback_filename
    )

    if fallback_path.exists():

        return {
            "found": True,
            "filename":
                fallback_filename,
            "path":
                fallback_path,
            "renamed": False,
        }

    return {
        "found": False,
        "filename":
            requested_filename,
        "path":
            requested_path,
        "renamed": False,
    }


# =========================================================
# BACKUP PAPERS.JSON
# =========================================================

def create_backup():

    if not PAPERS_DATABASE_FILE.exists():

        return

    shutil.copy2(
        PAPERS_DATABASE_FILE,
        BACKUP_FILE,
    )


# =========================================================
# CREATE MARKDOWN REPORT
# =========================================================

def create_report(
    results,
):

    lines = []

    lines.append(
        "# Approved Papers Merge Report"
    )

    lines.append("")

    lines.append(
        "This report records the approved-paper PDF "
        "verification and metadata merge."
    )

    lines.append("")

    lines.append(
        "No candidate in this report is considered "
        "full-text verified until the Evidence Extractor "
        "processes its PDF."
    )

    lines.append("")

    lines.append(
        "## Summary"
    )

    lines.append("")

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

    conflict = sum(
        1
        for item in results
        if item[
            "status"
        ] == "CITATION_KEY_CONFLICT"
    )

    lines.append(
        f"- Added: {added}"
    )

    lines.append(
        f"- Already present: {existing}"
    )

    lines.append(
        f"- Missing PDF: {missing}"
    )

    lines.append(
        f"- Citation-key conflicts: {conflict}"
    )

    lines.append("")

    lines.append(
        "## Paper Status"
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

    # -----------------------------------------------------
    # DETAILS
    # -----------------------------------------------------

    for item in results:

        lines.append(
            f"### {item.get('citation_key')}"
        )

        lines.append("")

        lines.append(
            f"- Title: "
            f"{item.get('title')}"
        )

        lines.append(
            f"- Status: "
            f"**{item.get('status')}**"
        )

        lines.append(
            f"- PDF: "
            f"`{item.get('pdf_filename')}`"
        )

        message = item.get(
            "message"
        )

        if message:

            lines.append(
                f"- Note: {message}"
            )

        lines.append("")

    MERGE_REPORT_FILE.write_text(
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
        "MERGING APPROVED PAPERS"
    )

    print(
        "========================================"
    )

    print()

    # -----------------------------------------------------
    # LOAD APPROVED PAPERS
    # -----------------------------------------------------

    try:

        approved = (
            load_approved_papers()
        )

    except FileNotFoundError as error:

        print(error)

        print()

        print(
            "Run first:"
        )

        print()

        print(
            "python approve_candidate_papers.py"
        )

        return

    if not approved:

        print(
            "No approved candidates found."
        )

        return

    # -----------------------------------------------------
    # LOAD CURRENT DATABASE
    # -----------------------------------------------------

    database = (
        load_papers_database()
    )

    papers = database.get(
        "papers",
        []
    )

    # -----------------------------------------------------
    # BACKUP BEFORE CHANGING ANYTHING
    # -----------------------------------------------------

    create_backup()

    # -----------------------------------------------------
    # LOOKUPS
    # -----------------------------------------------------

    (
        doi_lookup,
        title_lookup,
        citation_key_lookup,
    ) = build_existing_lookups(
        papers
    )

    # -----------------------------------------------------
    # PROCESS APPROVED PAPERS
    # -----------------------------------------------------

    results = []

    downloaded_records = []

    for candidate in approved:

        title = candidate.get(
            "title",
            ""
        )

        citation_key = candidate.get(
            "citation_key"
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
        # CHECK PDF FIRST
        # -------------------------------------------------

        pdf_result = check_pdf(
            candidate
        )

        pdf_filename = (
            pdf_result[
                "filename"
            ]
        )

        if not pdf_result[
            "found"
        ]:

            print(
                "PDF STATUS: MISSING"
            )

            print(
                f"Expected:"
            )

            print(
                pdf_result[
                    "path"
                ]
            )

            results.append(
                {
                    "citation_key":
                        citation_key,

                    "title":
                        title,

                    "pdf_filename":
                        pdf_filename,

                    "status":
                        "MISSING_PDF",

                    "message":
                        (
                            "Approved candidate was not "
                            "merged because the expected "
                            "PDF was not found."
                        ),
                }
            )

            print()

            continue

        print(
            "PDF STATUS: FOUND"
        )

        print(
            pdf_result[
                "path"
            ]
        )

        # -------------------------------------------------
        # CHECK EXISTING DOI/TITLE
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
            )

            print(
                "DATABASE STATUS: "
                "ALREADY PRESENT"
            )

            print(
                f"Existing citation key: "
                f"{existing_key}"
            )

            results.append(
                {
                    "citation_key":
                        existing_key
                        or citation_key,

                    "title":
                        title,

                    "pdf_filename":
                        pdf_filename,

                    "status":
                        "ALREADY_PRESENT",

                    "message":
                        reason,
                }
            )

            downloaded_records.append(
                {
                    "citation_key":
                        existing_key
                        or citation_key,

                    "title":
                        title,

                    "pdf_filename":
                        pdf_filename,
                }
            )

            print()

            continue

        # -------------------------------------------------
        # CITATION KEY COLLISION
        # -------------------------------------------------

        if (
            citation_key
            in citation_key_lookup
        ):

            collision_paper = (
                citation_key_lookup[
                    citation_key
                ]
            )

            print(
                "DATABASE STATUS: "
                "CITATION KEY CONFLICT"
            )

            print(
                "Existing title:"
            )

            print(
                collision_paper.get(
                    "title"
                )
            )

            results.append(
                {
                    "citation_key":
                        citation_key,

                    "title":
                        title,

                    "pdf_filename":
                        pdf_filename,

                    "status":
                        "CITATION_KEY_CONFLICT",

                    "message":
                        (
                            "The citation key is already "
                            "used by another publication. "
                            "Paper was not merged."
                        ),
                }
            )

            print()

            continue

        # -------------------------------------------------
        # CONVERT RECORD
        # -------------------------------------------------

        record = (
            convert_candidate_to_paper_record(
                candidate
            )
        )

        papers.append(
            record
        )

        # Update lookups immediately so later candidates
        # cannot create duplicates.

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

        citation_key_lookup[
            citation_key
        ] = record

        downloaded_records.append(
            {
                "citation_key":
                    citation_key,

                "title":
                    title,

                "pdf_filename":
                    pdf_filename,
            }
        )

        results.append(
            {
                "citation_key":
                    citation_key,

                "title":
                    title,

                "pdf_filename":
                    pdf_filename,

                "status":
                    "ADDED",

                "message":
                    (
                        "Metadata added as "
                        "CANDIDATE_METADATA_ONLY. "
                        "Full-text extraction is still "
                        "required."
                    ),
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
    # SAVE DOWNLOADED APPROVED DATABASE
    # -----------------------------------------------------

    downloaded_database = {
        "papers":
            downloaded_records
    }

    DOWNLOADED_DATABASE_FILE.write_text(
        json.dumps(
            downloaded_database,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # REPORT
    # -----------------------------------------------------

    create_report(
        results
    )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    added_count = sum(
        1
        for item in results
        if item[
            "status"
        ] == "ADDED"
    )

    existing_count = sum(
        1
        for item in results
        if item[
            "status"
        ] == "ALREADY_PRESENT"
    )

    missing_count = sum(
        1
        for item in results
        if item[
            "status"
        ] == "MISSING_PDF"
    )

    conflict_count = sum(
        1
        for item in results
        if item[
            "status"
        ] == "CITATION_KEY_CONFLICT"
    )

    print(
        "========================================"
    )

    print(
        "MERGE SUMMARY"
    )

    print(
        "========================================"
    )

    print()

    print(
        f"Added:                "
        f"{added_count}"
    )

    print(
        f"Already present:      "
        f"{existing_count}"
    )

    print(
        f"Missing PDFs:         "
        f"{missing_count}"
    )

    print(
        f"Citation conflicts:   "
        f"{conflict_count}"
    )

    print()

    print(
        "Database:"
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
        "Merge report:"
    )

    print(
        MERGE_REPORT_FILE
    )

    print()

    print(
        "Downloaded-paper list:"
    )

    print(
        DOWNLOADED_DATABASE_FILE
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "These papers are still NOT "
        "FULL_TEXT_VERIFIED."
    )

    print(
        "The Evidence Extractor must process "
        "each PDF next."
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()