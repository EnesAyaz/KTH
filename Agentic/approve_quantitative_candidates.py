import json
import re
from pathlib import Path


# =========================================================
# PROJECT PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"
PAPERS_DIR = ROOT_DIR / "papers"


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


TRIAGE_FILE = (
    DATA_DIR
    / "quantitative_candidate_triage.json"
)

PAPERS_FILE = (
    DATA_DIR
    / "papers.json"
)

APPROVED_FILE = (
    DATA_DIR
    / "approved_quantitative_candidates.json"
)

DOWNLOAD_MD_FILE = (
    OUTPUT_DIR
    / "quantitative_papers_to_download.md"
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
# EXISTING PAPERS
# =========================================================

def extract_papers(
    database,
):

    if isinstance(
        database,
        list,
    ):

        return database

    if isinstance(
        database,
        dict,
    ):

        return database.get(
            "papers",
            []
        )

    return []


def build_existing_sets():

    database = load_json(
        PAPERS_FILE,
        {
            "papers": []
        },
    )

    papers = extract_papers(
        database
    )

    existing_dois = set()

    existing_titles = set()

    existing_keys = set()

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

        key = paper.get(
            "citation_key"
        )

        if doi:
            existing_dois.add(
                doi
            )

        if title:
            existing_titles.add(
                title
            )

        if key:
            existing_keys.add(
                key
            )

    return (
        existing_dois,
        existing_titles,
        existing_keys,
    )


# =========================================================
# AUTHOR / CITATION KEY
# =========================================================

def extract_first_author_surname(
    authors,
):
    """
    Create a reasonable citation-key surname from the
    first author.

    Examples:

    "John Smith" -> Smith
    "Smith, John" -> Smith
    "J. Smith" -> Smith
    """

    if not authors:
        return "record"

    first_author = str(
        authors[0]
    ).strip()

    if not first_author:
        return "record"

    # Crossref-style:
    # "Smith, John"
    if "," in first_author:

        surname = (
            first_author
            .split(",")[0]
            .strip()
        )

    else:

        parts = (
            first_author
            .replace(
                ".",
                " "
            )
            .split()
        )

        if not parts:
            return "record"

        surname = (
            parts[-1]
        )

    surname = re.sub(
        r"[^A-Za-z0-9]",
        "",
        surname,
    )

    if not surname:
        return "record"

    return surname


def base_citation_key(
    candidate,
):

    surname = (
        extract_first_author_surname(
            candidate.get(
                "authors",
                []
            )
        )
    )

    year = candidate.get(
        "year"
    )

    if year is None:
        year = "Unknown"

    return (
        f"{surname}{year}"
    )


def unique_citation_key(
    base_key,
    used_keys,
):

    if (
        base_key
        not in used_keys
    ):

        used_keys.add(
            base_key
        )

        return base_key

    # Try a, b, c, ...
    for letter in (
        "abcdefghijklmnopqrstuvwxyz"
    ):

        candidate_key = (
            f"{base_key}{letter}"
        )

        if (
            candidate_key
            not in used_keys
        ):

            used_keys.add(
                candidate_key
            )

            return candidate_key

    # Extreme fallback
    counter = 2

    while True:

        candidate_key = (
            f"{base_key}_{counter}"
        )

        if (
            candidate_key
            not in used_keys
        ):

            used_keys.add(
                candidate_key
            )

            return candidate_key

        counter += 1


# =========================================================
# SELECTION PARSER
# =========================================================

def parse_selection(
    text,
    valid_ranks,
):
    """
    Accept:

    1,2,3,5
    1-5
    1,3-6,8
    """

    text = (
        text
        .strip()
        .replace(
            " ",
            ""
        )
    )

    if not text:
        return []

    selected = set()

    parts = text.split(
        ","
    )

    for part in parts:

        if not part:
            continue

        if "-" in part:

            start_text, end_text = (
                part.split(
                    "-",
                    1,
                )
            )

            try:

                start = int(
                    start_text
                )

                end = int(
                    end_text
                )

            except ValueError:

                raise ValueError(
                    f"Invalid selection: {part}"
                )

            if start > end:

                start, end = (
                    end,
                    start,
                )

            for value in range(
                start,
                end + 1,
            ):

                selected.add(
                    value
                )

        else:

            try:

                selected.add(
                    int(
                        part
                    )
                )

            except ValueError:

                raise ValueError(
                    f"Invalid selection: {part}"
                )

    invalid = sorted(
        selected
        - valid_ranks
    )

    if invalid:

        raise ValueError(
            "Invalid rank(s): "
            + ", ".join(
                str(x)
                for x in invalid
            )
        )

    return sorted(
        selected
    )


# =========================================================
# DISPLAY
# =========================================================

def display_candidates(
    candidates,
):

    print(
        "RANKED QUANTITATIVE CANDIDATES"
    )

    print(
        "========================================"
    )

    print()

    for candidate in candidates:

        rank = candidate.get(
            "rank"
        )

        score = candidate.get(
            "score"
        )

        recommendation = (
            candidate.get(
                "recommendation"
            )
        )

        category = candidate.get(
            "architecture_category"
        )

        title = candidate.get(
            "title"
        )

        fields = candidate.get(
            "expected_quantitative_fields",
            [],
        )

        pairs = candidate.get(
            "matched_quantitative_pairs",
            [],
        )

        print(
            f"[{rank}] "
            f"Score {score} | "
            f"{recommendation}"
        )

        print(
            title
        )

        print(
            f"Category: {category}"
        )

        print(
            f"Useful fields: "
            f"{len(fields)}"
        )

        print(
            f"Useful pairs: "
            f"{len(pairs)}"
        )

        print(
            f"DOI: "
            f"{candidate.get('doi')}"
        )

        print()


# =========================================================
# FIND DEFAULT SELECTION
# =========================================================

def build_default_selection(
    candidates,
):
    """
    Build a conservative default list.

    Priority:
    - all DOWNLOAD FIRST papers
    - then reserve papers until approximately 6 papers
    """

    selected = []

    # -----------------------------------------------------
    # DOWNLOAD FIRST
    # -----------------------------------------------------

    for candidate in candidates:

        if (
            candidate.get(
                "recommendation"
            )
            == "DOWNLOAD FIRST"
        ):

            selected.append(
                candidate[
                    "rank"
                ]
            )

    # -----------------------------------------------------
    # TARGET ABOUT SIX PAPERS
    # -----------------------------------------------------

    if len(selected) < 6:

        for candidate in candidates:

            if (
                candidate.get(
                    "recommendation"
                )
                != "DOWNLOAD / RESERVE"
            ):

                continue

            rank = candidate[
                "rank"
            ]

            if rank in selected:
                continue

            selected.append(
                rank
            )

            if len(selected) >= 6:
                break

    # Avoid automatically suggesting too many.
    return sorted(
        selected[:8]
    )


# =========================================================
# CREATE APPROVED RECORD
# =========================================================

def create_approved_record(
    candidate,
    citation_key,
):

    return {
        "rank":
            candidate.get(
                "rank"
            ),

        "score":
            candidate.get(
                "score"
            ),

        "recommendation":
            candidate.get(
                "recommendation"
            ),

        "title":
            candidate.get(
                "title"
            ),

        "authors":
            candidate.get(
                "authors",
                []
            ),

        "year":
            candidate.get(
                "year"
            ),

        "journal_or_venue":
            candidate.get(
                "journal_or_venue"
            ),

        "doi":
            normalize_doi(
                candidate.get(
                    "doi"
                )
            ),

        "url":
            candidate.get(
                "url"
            ),

        "publication_type":
            candidate.get(
                "publication_type"
            ),

        "architecture_category":
            candidate.get(
                "architecture_category"
            ),

        "matched_topic_ids":
            candidate.get(
                "matched_topic_ids",
                []
            ),

        "expected_quantitative_fields":
            candidate.get(
                "expected_quantitative_fields",
                []
            ),

        "expected_quantitative_pairs":
            candidate.get(
                "expected_quantitative_pairs",
                []
            ),

        "matched_quantitative_pairs":
            candidate.get(
                "matched_quantitative_pairs",
                []
            ),

        "experimental_relevance":
            candidate.get(
                "experimental_relevance"
            ),

        "quantitative_relevance":
            candidate.get(
                "quantitative_relevance"
            ),

        "full_text_access_likelihood":
            candidate.get(
                "full_text_access_likelihood"
            ),

        "selection_rationale":
            candidate.get(
                "selection_rationale"
            ),

        "citation_key":
            citation_key,

        "pdf_filename":
            f"{citation_key}.pdf",

        "verification_status":
            "CANDIDATE_METADATA_ONLY",
    }


# =========================================================
# WRITE DOWNLOAD GUIDE
# =========================================================

def write_download_guide(
    approved,
):

    lines = []

    lines.append(
        "# Quantitative Papers Approved for Download"
    )

    lines.append("")

    lines.append(
        "These papers were selected from the "
        "quantitative-gap-driven literature search."
    )

    lines.append("")

    lines.append(
        "**Important:** downloading a PDF does not "
        "make its technical claims verified. Each PDF "
        "must later pass the full-text Evidence Extractor "
        "and deterministic evidence-quality checker."
    )

    lines.append("")

    lines.append(
        "## Download Instructions"
    )

    lines.append("")

    lines.append(
        "Download each selected publication as a PDF "
        "and place it in:"
    )

    lines.append("")

    lines.append(
        "`C:\\Github\\KTH\\Agentic\\papers\\`"
    )

    lines.append("")

    lines.append(
        "Use the exact filename shown for each paper."
    )

    lines.append("")

    # -----------------------------------------------------
    # SUMMARY TABLE
    # -----------------------------------------------------

    lines.append(
        "## Selected Papers"
    )

    lines.append("")

    lines.append(
        "| Rank | Citation Key | Filename | Category | Paper |"
    )

    lines.append(
        "|---:|---|---|---|---|"
    )

    for paper in approved:

        title = str(
            paper.get(
                "title",
                ""
            )
        ).replace(
            "|",
            "\\|"
        )

        lines.append(
            f"| {paper['rank']} "
            f"| `{paper['citation_key']}` "
            f"| `{paper['pdf_filename']}` "
            f"| {paper['architecture_category']} "
            f"| {title} |"
        )

    lines.append("")

    # -----------------------------------------------------
    # DETAILS
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
            f"- Rank: "
            f"{paper['rank']}"
        )

        lines.append(
            f"- Score: "
            f"{paper['score']}"
        )

        lines.append(
            f"- Citation key: "
            f"`{paper['citation_key']}`"
        )

        lines.append(
            f"- Save PDF as: "
            f"`{paper['pdf_filename']}`"
        )

        lines.append(
            f"- DOI: "
            f"{paper['doi']}"
        )

        lines.append(
            f"- Venue: "
            f"{paper['journal_or_venue']}"
        )

        lines.append(
            f"- Category: "
            f"{paper['architecture_category']}"
        )

        lines.append("")

        lines.append(
            "Expected useful quantitative fields:"
        )

        lines.append("")

        fields = paper.get(
            "expected_quantitative_fields",
            []
        )

        if fields:

            for field in fields:

                lines.append(
                    f"- `{field}`"
                )

        else:

            lines.append(
                "- None identified"
            )

        lines.append("")

        pairs = paper.get(
            "matched_quantitative_pairs",
            []
        )

        lines.append(
            "Potential figure pairs:"
        )

        lines.append("")

        if pairs:

            for pair in pairs:

                lines.append(
                    f"- {pair}"
                )

        else:

            lines.append(
                "- None identified"
            )

        lines.append("")

    DOWNLOAD_MD_FILE.write_text(
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
        "APPROVE QUANTITATIVE CANDIDATES"
    )

    print(
        "========================================"
    )

    print()

    # -----------------------------------------------------
    # INPUT
    # -----------------------------------------------------

    if not TRIAGE_FILE.exists():

        print(
            "ERROR:"
        )

        print(
            "Could not find:"
        )

        print(
            TRIAGE_FILE
        )

        print()

        print(
            "Run first:"
        )

        print()

        print(
            "python rank_quantitative_candidates.py"
        )

        return

    triage_database = load_json(
        TRIAGE_FILE,
        {},
    )

    candidates = (
        triage_database.get(
            "candidates",
            []
        )
    )

    if not candidates:

        print(
            "No ranked candidates found."
        )

        return

    # -----------------------------------------------------
    # EXISTING DATABASE
    # -----------------------------------------------------

    (
        existing_dois,
        existing_titles,
        existing_keys,
    ) = build_existing_sets()

    # -----------------------------------------------------
    # FILTER ANY LAST-MINUTE DUPLICATES
    # -----------------------------------------------------

    valid_candidates = []

    duplicates = []

    for candidate in candidates:

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
            and doi in existing_dois
        ):

            duplicates.append(
                (
                    candidate,
                    "DOI already exists in papers.json",
                )
            )

            continue

        if (
            title
            and title in existing_titles
        ):

            duplicates.append(
                (
                    candidate,
                    "Title already exists in papers.json",
                )
            )

            continue

        valid_candidates.append(
            candidate
        )

    # -----------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------

    display_candidates(
        valid_candidates
    )

    if duplicates:

        print(
            "AUTOMATICALLY EXCLUDED EXISTING PAPERS"
        )

        print(
            "----------------------------------------"
        )

        for candidate, reason in duplicates:

            print(
                f"{candidate.get('title')}"
            )

            print(
                f"Reason: {reason}"
            )

            print()

    # -----------------------------------------------------
    # DEFAULT
    # -----------------------------------------------------

    default_selection = (
        build_default_selection(
            valid_candidates
        )
    )

    default_text = ",".join(
        str(rank)
        for rank in default_selection
    )

    print(
        "========================================"
    )

    print(
        "SELECTION"
    )

    print(
        "========================================"
    )

    print()

    print(
        "Recommended default ranks:"
    )

    print(
        default_text
        if default_text
        else "None"
    )

    print()

    print(
        "Recommended total: approximately 5-8 papers."
    )

    print()

    print(
        "Examples:"
    )

    print(
        "1,2,3,4,5,6"
    )

    print(
        "1-6"
    )

    print(
        "1,2,4-7"
    )

    print()

    selection_text = input(
        (
            "Enter ranks to approve "
            f"[Enter = {default_text}]: "
        )
    ).strip()

    if not selection_text:

        selection_text = (
            default_text
        )

    valid_ranks = {
        candidate[
            "rank"
        ]
        for candidate
        in valid_candidates
    }

    try:

        selected_ranks = (
            parse_selection(
                selection_text,
                valid_ranks,
            )
        )

    except ValueError as error:

        print()

        print(
            "ERROR:"
        )

        print(error)

        return

    if not selected_ranks:

        print(
            "No papers selected."
        )

        return

    # -----------------------------------------------------
    # SELECT CANDIDATES
    # -----------------------------------------------------

    selected_candidates = [

        candidate

        for candidate
        in valid_candidates

        if (
            candidate[
                "rank"
            ]
            in selected_ranks
        )
    ]

    selected_candidates.sort(
        key=lambda item: (
            item[
                "rank"
            ]
        )
    )

    # -----------------------------------------------------
    # GENERATE COLLISION-SAFE CITATION KEYS
    # -----------------------------------------------------

    used_keys = set(
        existing_keys
    )

    approved = []

    for candidate in selected_candidates:

        base_key = (
            base_citation_key(
                candidate
            )
        )

        citation_key = (
            unique_citation_key(
                base_key,
                used_keys,
            )
        )

        record = (
            create_approved_record(
                candidate,
                citation_key,
            )
        )

        approved.append(
            record
        )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    output_database = {
        "approved_count":
            len(
                approved
            ),

        "source":
            "quantitative_candidate_triage.json",

        "verification_policy":
            (
                "Approved for PDF acquisition only. "
                "No technical claim is full-text "
                "verified at this stage."
            ),

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

    write_download_guide(
        approved
    )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    print()
    print(
        "========================================"
    )

    print(
        "APPROVED PAPERS"
    )

    print(
        "========================================"
    )

    print()

    for index, paper in enumerate(
        approved,
        start=1,
    ):

        print(
            f"{index}. "
            f"{paper['citation_key']}"
        )

        print(
            f"   {paper['title']}"
        )

        print(
            f"   Save as: "
            f"{paper['pdf_filename']}"
        )

        print()

    print(
        f"Approved count: "
        f"{len(approved)}"
    )

    print()

    print(
        "Files created:"
    )

    print(
        APPROVED_FILE
    )

    print(
        DOWNLOAD_MD_FILE
    )

    print()

    print(
        "NEXT:"
    )

    print()

    print(
        "Download only these approved PDFs into:"
    )

    print(
        PAPERS_DIR
    )

    print()

    print(
        "Use the exact generated filenames."
    )

    print()

    print(
        "Do NOT modify papers.json manually."
    )

    print(
        "The next step will verify the files and "
        "safely ingest their metadata."
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()