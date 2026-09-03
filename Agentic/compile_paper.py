import shutil
import subprocess
from pathlib import Path


# =========================================================
# PROJECT PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = (
    ROOT_DIR
    / "output"
)

TEX_FILE = (
    OUTPUT_DIR
    / "review_paper.tex"
)

PDF_FILE = (
    OUTPUT_DIR
    / "review_paper.pdf"
)

LOG_FILE = (
    OUTPUT_DIR
    / "review_paper.log"
)


# =========================================================
# RUN COMMAND
# =========================================================

def run_command(command):
    """
    Run a command inside the output directory.

    Returns True when the command exits successfully.
    """

    print()
    print("Running:")
    print(" ".join(command))
    print()

    result = subprocess.run(
        command,
        cwd=OUTPUT_DIR,
        text=True,
    )

    return (
        result.returncode == 0
    )


# =========================================================
# CHECK PROGRAM
# =========================================================

def program_exists(name):
    """
    Check whether an executable is available in PATH.
    """

    return (
        shutil.which(name)
        is not None
    )


# =========================================================
# LATEXMK COMPILATION
# =========================================================

def compile_with_latexmk():
    """
    Compile using latexmk.

    latexmk requires Perl on Windows when using MiKTeX.
    """

    print()
    print("Using latexmk.")
    print()

    return run_command(
        [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-file-line-error",
            TEX_FILE.name,
        ]
    )


# =========================================================
# PDFLATEX + BIBTEX COMPILATION
# =========================================================

def compile_manually():
    """
    Compile using:

    pdflatex
        ↓
    bibtex
        ↓
    pdflatex
        ↓
    pdflatex
    """

    print()
    print(
        "Using manual compilation:"
    )

    print(
        "pdflatex -> bibtex -> "
        "pdflatex -> pdflatex"
    )

    print()

    # -----------------------------------------------------
    # FIRST PDFLATEX PASS
    # -----------------------------------------------------

    print(
        "PASS 1: pdflatex"
    )

    first_pass = run_command(
        [
            "pdflatex",
            "-interaction=nonstopmode",
            "-file-line-error",
            TEX_FILE.name,
        ]
    )

    if not first_pass:

        print()
        print(
            "First pdflatex pass failed."
        )

        return False

    # -----------------------------------------------------
    # BIBTEX
    # -----------------------------------------------------

    print()
    print(
        "PASS 2: bibtex"
    )

    bibtex_success = run_command(
        [
            "bibtex",
            TEX_FILE.stem,
        ]
    )

    if not bibtex_success:

        print()
        print(
            "BibTeX returned an error or warning."
        )

        print(
            "This may happen when there are currently "
            "no citations or references."
        )

        print(
            "Continuing with LaTeX compilation."
        )

    # -----------------------------------------------------
    # SECOND PDFLATEX PASS
    # -----------------------------------------------------

    print()
    print(
        "PASS 3: pdflatex"
    )

    second_pass = run_command(
        [
            "pdflatex",
            "-interaction=nonstopmode",
            "-file-line-error",
            TEX_FILE.name,
        ]
    )

    if not second_pass:

        print()
        print(
            "Second pdflatex pass failed."
        )

        return False

    # -----------------------------------------------------
    # THIRD PDFLATEX PASS
    # -----------------------------------------------------

    print()
    print(
        "PASS 4: pdflatex"
    )

    third_pass = run_command(
        [
            "pdflatex",
            "-interaction=nonstopmode",
            "-file-line-error",
            TEX_FILE.name,
        ]
    )

    if not third_pass:

        print()
        print(
            "Third pdflatex pass failed."
        )

        return False

    return True


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print(
        "========================================"
    )

    print(
        "COMPILING REVIEW PAPER"
    )

    print(
        "========================================"
    )

    print()

    # -----------------------------------------------------
    # CHECK TEX FILE
    # -----------------------------------------------------

    if not TEX_FILE.exists():

        print(
            "review_paper.tex does not exist."
        )

        print()

        print(
            "Run this first:"
        )

        print()

        print(
            "python assemble_paper.py"
        )

        print()

        return

    # -----------------------------------------------------
    # CHECK AVAILABLE PROGRAMS
    # -----------------------------------------------------

    has_pdflatex = (
        program_exists(
            "pdflatex"
        )
    )

    has_bibtex = (
        program_exists(
            "bibtex"
        )
    )

    has_latexmk = (
        program_exists(
            "latexmk"
        )
    )

    has_perl = (
        program_exists(
            "perl"
        )
    )

    print(
        f"pdflatex available: {has_pdflatex}"
    )

    print(
        f"bibtex available:   {has_bibtex}"
    )

    print(
        f"latexmk available:  {has_latexmk}"
    )

    print(
        f"Perl available:     {has_perl}"
    )

    print()

    # -----------------------------------------------------
    # PREFERRED METHOD:
    # LATEXMK ONLY WHEN PERL EXISTS
    # -----------------------------------------------------

    if (
        has_latexmk
        and has_perl
    ):

        print(
            "latexmk and Perl are available."
        )

        success = (
            compile_with_latexmk()
        )

    # -----------------------------------------------------
    # FALLBACK:
    # PDFLATEX + BIBTEX
    # -----------------------------------------------------

    elif (
        has_pdflatex
        and has_bibtex
    ):

        if (
            has_latexmk
            and not has_perl
        ):

            print(
                "latexmk was found, but Perl "
                "is not installed."
            )

            print(
                "Skipping latexmk."
            )

            print()

        success = (
            compile_manually()
        )

    # -----------------------------------------------------
    # NOTHING AVAILABLE
    # -----------------------------------------------------

    else:

        print(
            "Required LaTeX tools were not found."
        )

        print()

        print(
            "Required:"
        )

        print(
            "- pdflatex"
        )

        print(
            "- bibtex"
        )

        print()

        print(
            "Make sure MiKTeX is installed "
            "and available in PATH."
        )

        print()

        return

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    print()
    print(
        "========================================"
    )

    if (
        success
        and PDF_FILE.exists()
    ):

        print(
            "COMPILATION SUCCESSFUL"
        )

        print(
            "========================================"
        )

        print()

        print(
            "PDF created:"
        )

        print()

        print(
            PDF_FILE
        )

    else:

        print(
            "COMPILATION FAILED"
        )

        print(
            "========================================"
        )

        print()

        if LOG_FILE.exists():

            print(
                "Check the LaTeX log:"
            )

            print()

            print(
                LOG_FILE
            )

        else:

            print(
                "No LaTeX log file was generated."
            )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()