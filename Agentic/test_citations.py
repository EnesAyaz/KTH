import sys
from pathlib import Path

from tools.citation_checker import (
    check_citations,
)


# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

EVIDENCE_FILE = (
    ROOT_DIR
    / "data"
    / "evidence.json"
)


# =========================================================
# SELECT FILE
# =========================================================

if len(sys.argv) > 1:

    filename = sys.argv[1]

else:

    filename = "converter_architecture.tex"


LATEX_FILE = (
    ROOT_DIR
    / "output"
    / "sections"
    / filename
)


# =========================================================
# CHECK
# =========================================================

if not LATEX_FILE.exists():

    print()
    print(
        f"File not found: {LATEX_FILE}"
    )
    print()

    raise SystemExit(1)


result = check_citations(
    LATEX_FILE,
    EVIDENCE_FILE,
)


# =========================================================
# REPORT
# =========================================================

print()
print("==============================")
print("CITATION CHECK")
print("==============================")
print()

print("File:")
print(LATEX_FILE)
print()


print("Allowed citations:")

for citation in sorted(
    result["allowed"]
):
    print(
        f"  {citation}"
    )


print()
print("Used citations:")

for citation in sorted(
    result["used"]
):
    print(
        f"  {citation}"
    )


print()
print("Invalid citations:")

if not result["invalid"]:

    print(
        "  None."
    )

else:

    for citation in sorted(
        result["invalid"]
    ):

        print(
            f"  INVALID: {citation}"
        )


print()
print("==============================")

if result["invalid"]:

    print(
        "RESULT: FAILED"
    )

    raise SystemExit(1)

else:

    print(
        "RESULT: PASSED"
    )

print("==============================")
print()