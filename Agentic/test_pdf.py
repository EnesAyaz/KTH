from tools.pdf_tools import (
    list_local_papers,
    read_pdf_pages,
    search_pdf,
)


print(
    list_local_papers.__wrapped__()
)

print(
    search_pdf.__wrapped__(
        "Jin2017.pdf",
        "loss"
    )
)