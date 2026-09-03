import json
import re
from pathlib import Path


# =========================================================
# PATHS
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

TRIAGE_FILE = (
    DATA_DIR
    / "candidate_triage.json"
)

APPROVED_FILE = (
    DATA_DIR
    / "approved_candidates.json"
)

DOWNLOAD_REPORT_FILE = (
    OUTPUT_DIR
    / "approved_papers_to_download.md"
)


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# LOAD JSON
# =========================================================

def load_json(path):

    if not path.exists():

        raise FileNotFoundError(
            f"Could not find:\n{path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


# =========================================================
# CLEAN AUTHOR FAMILY NAME
# =========================================================

def clean_name(text):

    if not text:
        return "Paper"

    # If name is "First Last", use final word.
    parts = str(text).strip().split()

    if not parts:
        return "Paper"

    family_name = parts[-1]

    family_name = re.sub(
        r"[^A-Za-z0-9]",
        "",
        family_name,
    )

    if not family_name:
        return "Paper"

    return family_name


# =========================================================
# GENERATE CITATION KEY
# =========================================================

def generate_citation_key(
    paper,
    existing_keys,
):

    authors = paper.get(
        "authors",
        []
    )

    year = paper.get(
        "year"
    )

    if authors:

        base_name = clean_name(
            authors[0]
        )

    else:

        base_name = "Paper"

    if year is None:

        base_key = (
            f"{base_name}Unknown"
        )

    else:

        base_key = (
            f"{base_name}{year}"
        )

    candidate_key = base_key

    suffix_index = 0

    while (
        candidate_key
        in existing_keys
    ):

        suffix_index += 1

        suffix = chr(
            ord("a")
            + suffix_index
            - 1
        )

        candidate_key = (
            f"{base_key}{suffix}"
        )

    existing_keys.add(
        candidate_key
    )

    return candidate_key


# =========================================================
# SAFE PDF FILENAME
# =========================================================

def create_pdf_filename(
    citation_key
):

    safe = re.sub(
        r"[^A-Za-z0-9_-]",
        "",
        citation_key,
    )

    return (
        f"{safe}.pdf"
    )


# =========================================================
# PARSE USER SELECTION
# =========================================================

def parse_selection(
    text,
    maximum,
):

    selected = []

    pieces = (
        text
        .replace(
            " ",
            ""
        )
        .split(",")
    )

    for piece in pieces:

        if not piece:
            continue

        # Support:
        #
        # 1,2,4
        #
        # and:
        #
        # 1-4

        if "-" in piece:

            parts = piece.split(
                "-",
                1,
            )

            try:

                start = int(
                    parts[0]
                )

                end = int(
                    parts[1]
                )

            except ValueError:

                continue

            for value in range(
                start,
                end + 1,
            ):

                if (
                    1
                    <= value
                    <= maximum
                ):

                    selected.append(
                        value
                    )

        else:

            try:

                value = int(
                    piece
                )

            except ValueError:

                continue

            if (
                1
                <= value
                <= maximum
            ):

                selected.append(
                    value
                )

    # Remove duplicates while preserving order.

    unique = []

    seen = set()

    for value in selected:

        if value not in seen:

            unique.append(
                value
            )

            seen.add(
                value
            )

    return unique


# =========================================================
# CREATE DOWNLOAD REPORT
# =========================================================

def create_report(
    approved
):

    lines = []

    lines.append(
        "# Approved Papers to Download"
    )

    lines.append("")

    lines.append(
        "These papers have passed the human approval "
        "checkpoint."
    )

    lines.append("")

    lines.append(
        "**They are still NOT full-text verified.**"
    )

    lines.append("")

    lines.append(
        "Download each PDF and save it using the exact "
        "filename shown below."
    )

    lines.append("")

    lines.append(
        "Place all PDFs in:"
    )

    lines.append("")

    lines.append(
        "`papers/`"
    )

    lines.append("")

    # -----------------------------------------------------
    # PAPERS
    # -----------------------------------------------------

    for index, paper in enumerate(
        approved,
        start=1,
    ):

        lines.append(
            f"## {index}. "
            f"{paper['title']}"
        )

        lines.append("")

        lines.append(
            f"- Proposed citation key: "
            f"`{paper['citation_key']}`"
        )

        lines.append(
            f"- Required PDF filename: "
            f"`{paper['pdf_filename']}`"
        )

        doi = paper.get(
            "doi"
        )

        if doi:

            lines.append(
                f"- DOI: `{doi}`"
            )

        url = paper.get(
            "url"
        )

        if url:

            lines.append(
                f"- URL: {url}"
            )

        year = paper.get(
            "year"
        )

        if year is not None:

            lines.append(
                f"- Year: {year}"
            )

        venue = paper.get(
            "journal_or_venue"
        )

        if venue:

            lines.append(
                f"- Venue: {venue}"
            )

        lines.append(
            f"- Priority: "
            f"{paper.get('priority')}"
        )

        lines.append(
            f"- Original triage score: "
            f"{paper.get('triage_score')}"
        )

        lines.append("")

        useful_fields = paper.get(
            "expected_useful_fields",
            []
        )

        if useful_fields:

            lines.append(
                "Potentially useful fields:"
            )

            lines.append("")

            for field in useful_fields:

                lines.append(
                    f"- `{field}`"
                )

            lines.append("")

        lines.append(
            "> Status: APPROVED FOR DOWNLOAD, "
            "NOT SCIENTIFICALLY VERIFIED"
        )

        lines.append("")

        lines.append("---")

        lines.append("")

    DOWNLOAD_REPORT_FILE.write_text(
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
        "HUMAN PAPER APPROVAL"
    )

    print(
        "========================================"
    )

    print()

    # -----------------------------------------------------
    # LOAD TRIAGE
    # -----------------------------------------------------

    try:

        database = load_json(
            TRIAGE_FILE
        )

    except FileNotFoundError as error:

        print(error)

        print()

        print(
            "Run first:"
        )

        print()

        print(
            "python triage_candidate_papers.py"
        )

        return

    candidates = database.get(
        "candidates",
        []
    )

    # -----------------------------------------------------
    # REMOVE DUPLICATES
    # -----------------------------------------------------

    selectable = [

        paper

        for paper in candidates

        if not paper.get(
            "is_duplicate",
            False,
        )
    ]

    if not selectable:

        print(
            "No non-duplicate candidates "
            "are available."
        )

        return

    # -----------------------------------------------------
    # DISPLAY CANDIDATES
    # -----------------------------------------------------

    print(
        "AVAILABLE CANDIDATES"
    )

    print(
        "----------------------------------------"
    )

    print()

    for index, paper in enumerate(
        selectable,
        start=1,
    ):

        print(
            f"{index}. "
            f"[{paper.get('priority')}]"
        )

        print(
            f"   {paper.get('title')}"
        )

        print(
            f"   Score: "
            f"{paper.get('triage_score')}"
        )

        doi = paper.get(
            "doi"
        )

        if doi:

            print(
                f"   DOI: {doi}"
            )

        print()

    # -----------------------------------------------------
    # HUMAN SELECTION
    # -----------------------------------------------------

    print(
        "Enter the paper numbers you want "
        "to approve."
    )

    print()

    print(
        "Examples:"
    )

    print(
        "1,2,3,5"
    )

    print(
        "or"
    )

    print(
        "1-6"
    )

    print()

    user_input = input(
        "Approved papers: "
    )

    selection = parse_selection(
        user_input,
        len(
            selectable
        ),
    )

    if not selection:

        print()
        print(
            "No valid papers selected."
        )

        return

    # -----------------------------------------------------
    # CREATE APPROVED RECORDS
    # -----------------------------------------------------

    approved = []

    existing_keys = set()

    for number in selection:

        original = dict(
            selectable[
                number - 1
            ]
        )

        citation_key = (
            generate_citation_key(
                original,
                existing_keys,
            )
        )

        pdf_filename = (
            create_pdf_filename(
                citation_key
            )
        )

        approved_record = {
            **original,

            "citation_key":
                citation_key,

            "pdf_filename":
                pdf_filename,

            "approval_status":
                "APPROVED_FOR_DOWNLOAD",

            "full_text_status":
                "NOT_DOWNLOADED_OR_NOT_VERIFIED",
        }

        approved.append(
            approved_record
        )

    # -----------------------------------------------------
    # SAVE JSON
    # -----------------------------------------------------

    output_database = {
        "approved_count":
            len(approved),

        "papers":
            approved,
    }

    APPROVED_FILE.write_text(
        json.dumps(
            output_database,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # SAVE MARKDOWN
    # -----------------------------------------------------

    create_report(
        approved
    )

    # -----------------------------------------------------
    # TERMINAL OUTPUT
    # -----------------------------------------------------

    print()
    print(
        "========================================"
    )

    print(
        "APPROVAL COMPLETE"
    )

    print(
        "========================================"
    )

    print()

    print(
        f"Approved papers: "
        f"{len(approved)}"
    )

    print()

    for paper in approved:

        print(
            paper[
                "citation_key"
            ]
        )

        print(
            f"  {paper['title']}"
        )

        print(
            f"  Save PDF as:"
        )

        print(
            f"  papers\\"
            f"{paper['pdf_filename']}"
        )

        print()

    print(
        "Files created:"
    )

    print()

    print(
        APPROVED_FILE
    )

    print(
        DOWNLOAD_REPORT_FILE
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "papers.json has NOT been modified."
    )

    print(
        "evidence.json has NOT been modified."
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()