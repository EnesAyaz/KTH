from tools.literature_tools import crossref_search


result = crossref_search.__wrapped__(
    "integrated modular motor drive traction"
)

print(result)