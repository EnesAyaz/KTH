from pathlib import Path

from paper_config import (
    PAPER_TITLE,
    AUTHOR_NAME,
    SECTIONS,
)


# =========================================================
# PROJECT PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = (
    ROOT_DIR
    / "output"
)

SECTIONS_DIR = (
    OUTPUT_DIR
    / "sections"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "review_paper.tex"
)


# =========================================================
# CREATE SECTION INPUT COMMANDS
# =========================================================

def build_section_inputs():
    """
    Create LaTeX \\input commands for every section that
    exists in output/sections/.

    If a section does not exist, create a placeholder in the
    main manuscript instead.
    """

    lines = []

    for section in SECTIONS:

        filename = section[
            "filename"
        ]

        title = section[
            "title"
        ]

        section_file = (
            SECTIONS_DIR
            / filename
        )

        # -------------------------------------------------
        # SECTION EXISTS
        # -------------------------------------------------

        if section_file.exists():

            # Remove .tex extension because LaTeX does not
            # require it in \input{...}
            latex_path = (
                "sections/"
                + Path(filename).stem
            )

            lines.append(
                f"\\input{{{latex_path}}}"
            )

        # -------------------------------------------------
        # SECTION DOES NOT EXIST
        # -------------------------------------------------

        else:

            lines.append("")

            lines.append(
                "% ==================================================="
            )

            lines.append(
                f"% MISSING SECTION: {title}"
            )

            lines.append(
                "% ==================================================="
            )

            lines.append("")

            lines.append(
                f"\\section{{{title}}}"
            )

            lines.append("")

            lines.append(
                "% ADDITIONAL LITERATURE REQUIRED"
            )

    return "\n\n".join(
        lines
    )


# =========================================================
# CREATE LATEX DOCUMENT
# =========================================================

def build_latex_document(
    section_inputs
):
    """
    Build the complete LaTeX manuscript.

    IMPORTANT:

    This intentionally does NOT use an f-string because
    LaTeX itself uses many {curly braces}. Using an f-string
    would make Python try to interpret LaTeX commands such as

        {IEEEtran}

    as Python expressions.

    Instead, simple placeholder strings are replaced after
    the template is created.
    """

    latex_template = r"""
\documentclass[journal]{IEEEtran}

% =========================================================
% PACKAGES
% =========================================================

\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{array}
\usepackage{siunitx}
\usepackage{cite}
\usepackage{url}


% =========================================================
% GRAPHICS PATH
% =========================================================

\graphicspath{{../figures/generated/}}


% =========================================================
% TITLE AND AUTHOR
% =========================================================

\title{__PAPER_TITLE__}

\author{__AUTHOR_NAME__}


% =========================================================
% DOCUMENT
% =========================================================

\begin{document}

\maketitle


% =========================================================
% ABSTRACT
% =========================================================

\begin{abstract}

% ABSTRACT WILL BE GENERATED AFTER THE MAIN PAPER IS COMPLETE.

\end{abstract}


% =========================================================
% KEYWORDS
% =========================================================

\begin{IEEEkeywords}

stacked polyphase bridge,
multiphase drives,
traction inverter,
GaN,
SiC,
integrated motor drive,
electric vehicles

\end{IEEEkeywords}


% =========================================================
% PAPER SECTIONS
% =========================================================

__SECTION_INPUTS__


% =========================================================
% REFERENCES
% =========================================================

\bibliographystyle{IEEEtran}

\bibliography{references}


\end{document}
"""

    # -----------------------------------------------------
    # REPLACE PLACEHOLDERS
    # -----------------------------------------------------

    latex = latex_template.replace(
        "__PAPER_TITLE__",
        PAPER_TITLE,
    )

    latex = latex.replace(
        "__AUTHOR_NAME__",
        AUTHOR_NAME,
    )

    latex = latex.replace(
        "__SECTION_INPUTS__",
        section_inputs,
    )

    # Remove leading blank line introduced by triple quotes.
    return latex.lstrip()


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print(
        "========================================"
    )

    print(
        "ASSEMBLING LATEX REVIEW PAPER"
    )

    print(
        "========================================"
    )

    print()

    # -----------------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # -----------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    SECTIONS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------------------------------
    # CREATE SECTION INPUT COMMANDS
    # -----------------------------------------------------

    section_inputs = (
        build_section_inputs()
    )

    # -----------------------------------------------------
    # BUILD COMPLETE DOCUMENT
    # -----------------------------------------------------

    latex = build_latex_document(
        section_inputs
    )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    OUTPUT_FILE.write_text(
        latex,
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # REPORT
    # -----------------------------------------------------

    existing_sections = 0

    missing_sections = 0

    for section in SECTIONS:

        section_file = (
            SECTIONS_DIR
            / section["filename"]
        )

        if section_file.exists():

            existing_sections += 1

        else:

            missing_sections += 1

    print(
        f"Sections found:   "
        f"{existing_sections}"
    )

    print(
        f"Sections missing: "
        f"{missing_sections}"
    )

    print()

    print(
        "LaTeX manuscript created:"
    )

    print(
        OUTPUT_FILE
    )

    print()

    if missing_sections > 0:

        print(
            "NOTE:"
        )

        print(
            "Missing sections were inserted as "
            "placeholders containing:"
        )

        print()

        print(
            "% ADDITIONAL LITERATURE REQUIRED"
        )

        print()

    print(
        "========================================"
    )

    print(
        "ASSEMBLY COMPLETE"
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