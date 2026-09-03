from pathlib import Path
import fitz

from agents.decorators import tool


ROOT_DIR = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT_DIR / "papers"


@tool
def list_local_papers() -> str:
    """
    List all PDF papers available in the local papers folder.
    """

    pdf_files = sorted(PAPER_DIR.glob("*.pdf"))

    if not pdf_files:
        return "No PDF files found."

    return "\n".join(
        file.name
        for file in pdf_files
    )


@tool
def read_pdf_pages(
    filename: str,
    start_page: int,
    end_page: int
) -> str:
    """
    Read a selected page range from a PDF.

    Args:
        filename: PDF filename including .pdf.
        start_page: First page to read, starting from 1.
        end_page: Last page to read.
    """

    path = PAPER_DIR / filename

    if not path.exists():
        return f"PDF not found: {filename}"

    document = fitz.open(path)

    start_index = max(
        0,
        start_page - 1
    )

    end_index = min(
        end_page,
        len(document)
    )

    output = []

    for page_index in range(
        start_index,
        end_index
    ):

        page = document[page_index]

        text = page.get_text()

        output.append(
            f"\n--- PAGE {page_index + 1} ---\n"
        )

        output.append(text)

    return "".join(output)


@tool
def search_pdf(
    filename: str,
    search_term: str
) -> str:
    """
    Search a PDF for a word or phrase and return matching pages.

    Args:
        filename: PDF filename including .pdf.
        search_term: Word or phrase to search for.
    """

    path = PAPER_DIR / filename

    if not path.exists():
        return f"PDF not found: {filename}"

    document = fitz.open(path)

    matches = []

    term = search_term.lower()

    for page_number, page in enumerate(
        document,
        start=1
    ):

        text = page.get_text()

        if term in text.lower():

            # Limit text returned to control token usage
            snippet = text[:2500]

            matches.append(
                f"""
PAGE {page_number}

{snippet}
"""
            )

    if not matches:

        return (
            f"No matches found for "
            f"'{search_term}' "
            f"in {filename}."
        )

    return "\n".join(matches[:10])