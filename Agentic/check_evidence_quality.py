import argparse
import json
import re
import sys
from pathlib import Path

import pymupdf


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

EVIDENCE_FILE = (
    DATA_DIR
    / "evidence.json"
)


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# ALLOWED VALUES
# =========================================================

ALLOWED_EVIDENCE_TYPES = {
    "definition",
    "method",
    "experimental_result",
    "numerical_result",
    "comparison",
    "limitation",
    "conclusion",
}


ALLOWED_VERIFICATION_LEVELS = {
    "FULL_TEXT_VERIFIED",
    "ABSTRACT_ONLY",
    "METADATA_ONLY",
}


ALLOWED_CONFIDENCE_LEVELS = {
    "high",
    "medium",
    "low",
}


# =========================================================
# LOAD JSON
# =========================================================

def load_json(path):
    """
    Load JSON and raise a useful error if the file is
    missing or invalid.
    """

    if not path.exists():

        raise FileNotFoundError(
            f"Could not find:\n{path}"
        )

    try:

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except json.JSONDecodeError as error:

        raise RuntimeError(
            f"Invalid JSON in:\n{path}\n\n{error}"
        )


# =========================================================
# FIND PAPER
# =========================================================

def find_paper(
    evidence_database,
    citation_key,
):

    matches = [

        paper

        for paper in evidence_database.get(
            "papers",
            []
        )

        if (
            paper.get(
                "citation_key"
            )
            == citation_key
        )
    ]

    return matches


# =========================================================
# NORMALIZE STATEMENT
# =========================================================

def normalize_statement(text):
    """
    Normalize a claim statement to help identify accidental
    duplicates.
    """

    if not text:
        return ""

    text = str(
        text
    ).lower()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    text = re.sub(
        r"[^\w\s]",
        "",
        text,
    )

    return text.strip()


# =========================================================
# PDF PAGE COUNT
# =========================================================

def get_pdf_page_count(
    pdf_path,
):

    if not pdf_path.exists():

        return None

    document = pymupdf.open(
        pdf_path
    )

    page_count = len(
        document
    )

    document.close()

    return page_count


# =========================================================
# ISSUE CREATION
# =========================================================

def add_issue(
    issues,
    severity,
    claim_id,
    message,
):
    """
    Add one structured quality-control issue.
    """

    issues.append(
        {
            "severity":
                severity,

            "claim_id":
                claim_id,

            "message":
                message,
        }
    )


# =========================================================
# CLAIM ID EXPECTATION
# =========================================================

def expected_claim_id(
    citation_key,
    index,
):

    return (
        f"{citation_key}_C"
        f"{index:02d}"
    )


# =========================================================
# CHECK ONE CLAIM
# =========================================================

def check_claim(
    claim,
    citation_key,
    expected_id,
    pdf_page_count,
    seen_claim_ids,
    seen_statements,
    issues,
):

    claim_id = (
        claim.get(
            "claim_id"
        )
        or "MISSING_CLAIM_ID"
    )

    # -----------------------------------------------------
    # CLAIM ID
    # -----------------------------------------------------

    if not claim.get(
        "claim_id"
    ):

        add_issue(
            issues,
            "CRITICAL",
            claim_id,
            "Claim ID is missing.",
        )

    else:

        if claim_id in seen_claim_ids:

            add_issue(
                issues,
                "CRITICAL",
                claim_id,
                (
                    "Duplicate claim ID detected."
                ),
            )

        seen_claim_ids.add(
            claim_id
        )

        if claim_id != expected_id:

            add_issue(
                issues,
                "WARNING",
                claim_id,
                (
                    f"Expected sequential claim ID "
                    f"`{expected_id}`, but found "
                    f"`{claim_id}`."
                ),
            )

    # -----------------------------------------------------
    # CITATION KEY
    # -----------------------------------------------------

    claim_citation_key = (
        claim.get(
            "citation_key"
        )
    )

    if (
        claim_citation_key
        != citation_key
    ):

        add_issue(
            issues,
            "CRITICAL",
            claim_id,
            (
                f"Claim citation key is "
                f"`{claim_citation_key}` but paper "
                f"citation key is `{citation_key}`."
            ),
        )

    # -----------------------------------------------------
    # STATEMENT
    # -----------------------------------------------------

    statement = (
        claim.get(
            "statement"
        )
    )

    if (
        statement is None
        or not str(
            statement
        ).strip()
    ):

        add_issue(
            issues,
            "CRITICAL",
            claim_id,
            "Claim statement is empty.",
        )

    else:

        normalized = (
            normalize_statement(
                statement
            )
        )

        if (
            normalized
            and normalized
            in seen_statements
        ):

            add_issue(
                issues,
                "WARNING",
                claim_id,
                (
                    "Claim statement appears to be an "
                    "exact duplicate of another claim."
                ),
            )

        if normalized:

            seen_statements.add(
                normalized
            )

    # -----------------------------------------------------
    # SOURCE TITLE
    # -----------------------------------------------------

    source_title = (
        claim.get(
            "source_title"
        )
    )

    if (
        source_title is None
        or not str(
            source_title
        ).strip()
    ):

        add_issue(
            issues,
            "WARNING",
            claim_id,
            "Source title is missing.",
        )

    # -----------------------------------------------------
    # EVIDENCE TYPE
    # -----------------------------------------------------

    evidence_type = (
        claim.get(
            "evidence_type"
        )
    )

    if (
        evidence_type
        not in ALLOWED_EVIDENCE_TYPES
    ):

        add_issue(
            issues,
            "CRITICAL",
            claim_id,
            (
                f"Invalid evidence type: "
                f"`{evidence_type}`."
            ),
        )

    # -----------------------------------------------------
    # VERIFICATION LEVEL
    # -----------------------------------------------------

    verification_level = (
        claim.get(
            "verification_level"
        )
    )

    if (
        verification_level
        not in ALLOWED_VERIFICATION_LEVELS
    ):

        add_issue(
            issues,
            "CRITICAL",
            claim_id,
            (
                f"Invalid verification level: "
                f"`{verification_level}`."
            ),
        )

    # -----------------------------------------------------
    # CONFIDENCE
    # -----------------------------------------------------

    confidence = (
        claim.get(
            "confidence"
        )
    )

    if (
        confidence
        not in ALLOWED_CONFIDENCE_LEVELS
    ):

        add_issue(
            issues,
            "CRITICAL",
            claim_id,
            (
                f"Invalid confidence level: "
                f"`{confidence}`."
            ),
        )

    # -----------------------------------------------------
    # PAGE NUMBER
    # -----------------------------------------------------

    page_number = (
        claim.get(
            "page_number"
        )
    )

    if (
        verification_level
        == "FULL_TEXT_VERIFIED"
    ):

        if page_number is None:

            add_issue(
                issues,
                "WARNING",
                claim_id,
                (
                    "FULL_TEXT_VERIFIED claim has no "
                    "page number."
                ),
            )

        elif not isinstance(
            page_number,
            int,
        ):

            add_issue(
                issues,
                "CRITICAL",
                claim_id,
                (
                    "Page number is not an integer."
                ),
            )

        elif page_number < 1:

            add_issue(
                issues,
                "CRITICAL",
                claim_id,
                (
                    f"Invalid page number: "
                    f"{page_number}."
                ),
            )

        elif (
            pdf_page_count is not None
            and page_number
            > pdf_page_count
        ):

            add_issue(
                issues,
                "CRITICAL",
                claim_id,
                (
                    f"Claim references page "
                    f"{page_number}, but PDF contains "
                    f"only {pdf_page_count} pages."
                ),
            )

    # -----------------------------------------------------
    # SUPPORTING EXCERPT
    # -----------------------------------------------------

    supporting_excerpt = (
        claim.get(
            "supporting_excerpt"
        )
    )

    if (
        verification_level
        == "FULL_TEXT_VERIFIED"
    ):

        if (
            supporting_excerpt is None
            or not str(
                supporting_excerpt
            ).strip()
        ):

            add_issue(
                issues,
                "WARNING",
                claim_id,
                (
                    "FULL_TEXT_VERIFIED claim has no "
                    "supporting excerpt."
                ),
            )

    # -----------------------------------------------------
    # RELEVANT SECTIONS
    # -----------------------------------------------------

    relevant_sections = (
        claim.get(
            "relevant_sections",
            []
        )
    )

    if not isinstance(
        relevant_sections,
        list,
    ):

        add_issue(
            issues,
            "CRITICAL",
            claim_id,
            (
                "relevant_sections is not a list."
            ),
        )

    elif len(
        relevant_sections
    ) == 0:

        add_issue(
            issues,
            "WARNING",
            claim_id,
            (
                "No relevant review-paper section "
                "assigned."
            ),
        )

    # -----------------------------------------------------
    # NUMERICAL VALUES
    # -----------------------------------------------------

    numerical_values = (
        claim.get(
            "numerical_values",
            []
        )
    )

    if not isinstance(
        numerical_values,
        list,
    ):

        add_issue(
            issues,
            "CRITICAL",
            claim_id,
            (
                "numerical_values is not a list."
            ),
        )

        numerical_values = []

    # -----------------------------------------------------
    # NUMERICAL RESULT QUALITY
    # -----------------------------------------------------

    if (
        evidence_type
        == "numerical_result"
    ):

        if len(
            numerical_values
        ) == 0:

            add_issue(
                issues,
                "WARNING",
                claim_id,
                (
                    "Claim is classified as "
                    "`numerical_result` but contains "
                    "no numerical_values."
                ),
            )

    # -----------------------------------------------------
    # NUMERICAL TRACEABILITY
    # -----------------------------------------------------

    if (
        len(
            numerical_values
        ) > 0
    ):

        if page_number is None:

            add_issue(
                issues,
                "WARNING",
                claim_id,
                (
                    "Numerical values are present but "
                    "no page number is provided."
                ),
            )

        if (
            supporting_excerpt is None
            or not str(
                supporting_excerpt
            ).strip()
        ):

            add_issue(
                issues,
                "WARNING",
                claim_id,
                (
                    "Numerical values are present but "
                    "no supporting excerpt is provided."
                ),
            )


# =========================================================
# CHECK PAPER
# =========================================================

def check_paper(
    paper,
):

    citation_key = (
        paper.get(
            "citation_key"
        )
    )

    title = (
        paper.get(
            "title",
            ""
        )
    )

    pdf_filename = (
        paper.get(
            "pdf_filename"
        )
    )

    issues = []

    # -----------------------------------------------------
    # PAPER METADATA
    # -----------------------------------------------------

    if not citation_key:

        add_issue(
            issues,
            "CRITICAL",
            "PAPER",
            "Paper citation key is missing.",
        )

    if not title:

        add_issue(
            issues,
            "CRITICAL",
            "PAPER",
            "Paper title is missing.",
        )

    if not pdf_filename:

        add_issue(
            issues,
            "WARNING",
            "PAPER",
            "pdf_filename is missing.",
        )

        pdf_path = None

        pdf_page_count = None

    else:

        pdf_path = (
            PAPERS_DIR
            / pdf_filename
        )

        if not pdf_path.exists():

            add_issue(
                issues,
                "CRITICAL",
                "PAPER",
                (
                    f"PDF file does not exist: "
                    f"{pdf_path}"
                ),
            )

            pdf_page_count = None

        else:

            try:

                pdf_page_count = (
                    get_pdf_page_count(
                        pdf_path
                    )
                )

            except Exception as error:

                add_issue(
                    issues,
                    "CRITICAL",
                    "PAPER",
                    (
                        "Could not open PDF using "
                        f"PyMuPDF: {error}"
                    ),
                )

                pdf_page_count = None

    # -----------------------------------------------------
    # CLAIMS
    # -----------------------------------------------------

    claims = (
        paper.get(
            "claims",
            []
        )
    )

    if not isinstance(
        claims,
        list,
    ):

        add_issue(
            issues,
            "CRITICAL",
            "PAPER",
            "claims is not a list.",
        )

        claims = []

    if len(
        claims
    ) == 0:

        add_issue(
            issues,
            "CRITICAL",
            "PAPER",
            "Paper contains no extracted claims.",
        )

    seen_claim_ids = set()

    seen_statements = set()

    for index, claim in enumerate(
        claims,
        start=1,
    ):

        expected_id = (
            expected_claim_id(
                citation_key,
                index,
            )
        )

        check_claim(
            claim,
            citation_key,
            expected_id,
            pdf_page_count,
            seen_claim_ids,
            seen_statements,
            issues,
        )

    return {
        "citation_key":
            citation_key,

        "title":
            title,

        "pdf_filename":
            pdf_filename,

        "pdf_page_count":
            pdf_page_count,

        "claim_count":
            len(
                claims
            ),

        "full_text_claims":
            sum(
                1
                for claim in claims
                if (
                    claim.get(
                        "verification_level"
                    )
                    == "FULL_TEXT_VERIFIED"
                )
            ),

        "numerical_claims":
            sum(
                1
                for claim in claims
                if len(
                    claim.get(
                        "numerical_values",
                        []
                    )
                ) > 0
            ),

        "unresolved_questions":
            paper.get(
                "unresolved_questions",
                []
            ),

        "issues":
            issues,
    }


# =========================================================
# COUNT SEVERITY
# =========================================================

def count_severity(
    result,
    severity,
):

    return sum(
        1
        for issue in result[
            "issues"
        ]
        if (
            issue[
                "severity"
            ]
            == severity
        )
    )


# =========================================================
# FINAL STATUS
# =========================================================

def determine_status(
    result,
):

    critical = count_severity(
        result,
        "CRITICAL",
    )

    warnings = count_severity(
        result,
        "WARNING",
    )

    if critical > 0:

        return "FAIL"

    if warnings > 0:

        return "PASS WITH WARNINGS"

    return "PASS"


# =========================================================
# CREATE MARKDOWN REPORT
# =========================================================

def create_report(
    result,
):

    citation_key = (
        result[
            "citation_key"
        ]
    )

    report_file = (
        OUTPUT_DIR
        / (
            f"evidence_quality_"
            f"{citation_key}.md"
        )
    )

    status = determine_status(
        result
    )

    critical_count = (
        count_severity(
            result,
            "CRITICAL",
        )
    )

    warning_count = (
        count_severity(
            result,
            "WARNING",
        )
    )

    lines = []

    lines.append(
        f"# Evidence Quality Report — "
        f"{citation_key}"
    )

    lines.append("")

    lines.append(
        f"**Status:** {status}"
    )

    lines.append("")

    lines.append(
        f"- Title: {result['title']}"
    )

    lines.append(
        f"- PDF: `{result['pdf_filename']}`"
    )

    lines.append(
        f"- PDF pages: "
        f"{result['pdf_page_count']}"
    )

    lines.append(
        f"- Total claims: "
        f"{result['claim_count']}"
    )

    lines.append(
        f"- FULL_TEXT_VERIFIED claims: "
        f"{result['full_text_claims']}"
    )

    lines.append(
        f"- Claims containing numerical values: "
        f"{result['numerical_claims']}"
    )

    lines.append(
        f"- Critical issues: "
        f"{critical_count}"
    )

    lines.append(
        f"- Warnings: "
        f"{warning_count}"
    )

    lines.append("")

    # -----------------------------------------------------
    # ISSUES
    # -----------------------------------------------------

    lines.append(
        "## Issues"
    )

    lines.append("")

    if not result[
        "issues"
    ]:

        lines.append(
            "No deterministic structural issues detected."
        )

        lines.append("")

    else:

        for issue in result[
            "issues"
        ]:

            lines.append(
                f"### {issue['severity']} — "
                f"{issue['claim_id']}"
            )

            lines.append("")

            lines.append(
                issue[
                    "message"
                ]
            )

            lines.append("")

    # -----------------------------------------------------
    # UNRESOLVED QUESTIONS
    # -----------------------------------------------------

    lines.append(
        "## Unresolved Questions"
    )

    lines.append("")

    unresolved = (
        result.get(
            "unresolved_questions",
            []
        )
        or []
    )

    if unresolved:

        for question in unresolved:

            lines.append(
                f"- {question}"
            )

    else:

        lines.append(
            "- None recorded"
        )

    lines.append("")

    # -----------------------------------------------------
    # IMPORTANT NOTE
    # -----------------------------------------------------

    lines.append(
        "## Interpretation"
    )

    lines.append("")

    lines.append(
        "This deterministic check verifies structural "
        "consistency and traceability indicators. "
        "It does not prove that the scientific meaning "
        "of every extracted claim is correct."
    )

    lines.append("")

    lines.append(
        "High-value numerical claims should still be "
        "manually spot-checked against the PDF before "
        "final publication."
    )

    lines.append("")

    report_file.write_text(
        "\n".join(
            lines
        ),
        encoding="utf-8",
    )

    return report_file


# =========================================================
# MAIN
# =========================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Deterministically check extracted scientific "
            "evidence for one paper."
        )
    )

    parser.add_argument(
        "--key",
        type=str,
        required=True,
        help=(
            "Citation key to check, for example "
            "Rohner2024."
        ),
    )

    args = parser.parse_args()

    citation_key = (
        args.key
    )

    print()
    print(
        "========================================"
    )

    print(
        "EVIDENCE QUALITY CHECK"
    )

    print(
        "========================================"
    )

    print()

    # -----------------------------------------------------
    # LOAD DATABASE
    # -----------------------------------------------------

    try:

        database = (
            load_json(
                EVIDENCE_FILE
            )
        )

    except Exception as error:

        print(
            "ERROR:"
        )

        print(error)

        sys.exit(1)

    # -----------------------------------------------------
    # FIND PAPER
    # -----------------------------------------------------

    matches = find_paper(
        database,
        citation_key,
    )

    if len(
        matches
    ) == 0:

        print(
            f"ERROR:"
        )

        print(
            f"No evidence entry found for "
            f"`{citation_key}`."
        )

        sys.exit(1)

    if len(
        matches
    ) > 1:

        print(
            "ERROR:"
        )

        print(
            f"Multiple evidence entries found for "
            f"`{citation_key}`."
        )

        print(
            "This must be fixed before continuing."
        )

        sys.exit(1)

    paper = (
        matches[0]
    )

    # -----------------------------------------------------
    # CHECK
    # -----------------------------------------------------

    result = check_paper(
        paper
    )

    status = determine_status(
        result
    )

    critical_count = (
        count_severity(
            result,
            "CRITICAL",
        )
    )

    warning_count = (
        count_severity(
            result,
            "WARNING",
        )
    )

    # -----------------------------------------------------
    # REPORT
    # -----------------------------------------------------

    report_file = (
        create_report(
            result
        )
    )

    # -----------------------------------------------------
    # TERMINAL SUMMARY
    # -----------------------------------------------------

    print(
        f"Paper: "
        f"{citation_key}"
    )

    print()

    print(
        f"PDF pages:              "
        f"{result['pdf_page_count']}"
    )

    print(
        f"Total claims:           "
        f"{result['claim_count']}"
    )

    print(
        f"FULL_TEXT_VERIFIED:     "
        f"{result['full_text_claims']}"
    )

    print(
        f"Numerical claims:       "
        f"{result['numerical_claims']}"
    )

    print(
        f"Critical issues:        "
        f"{critical_count}"
    )

    print(
        f"Warnings:               "
        f"{warning_count}"
    )

    print()

    print(
        "========================================"
    )

    print(
        f"STATUS: {status}"
    )

    print(
        "========================================"
    )

    print()

    if result[
        "issues"
    ]:

        print(
            "ISSUES"
        )

        print(
            "----------------------------------------"
        )

        for issue in result[
            "issues"
        ]:

            print(
                f"[{issue['severity']}] "
                f"{issue['claim_id']}"
            )

            print(
                f"  {issue['message']}"
            )

            print()

    print(
        "Quality report:"
    )

    print(
        report_file
    )

    print()

    # -----------------------------------------------------
    # EXIT CODE
    # -----------------------------------------------------

    if critical_count > 0:

        sys.exit(1)

    sys.exit(0)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()