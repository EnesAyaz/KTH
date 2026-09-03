from tools.reference_tools import doi_to_bibtex


result = doi_to_bibtex.__wrapped__(
    "10.4271/2011-01-0344"
)

print(result)