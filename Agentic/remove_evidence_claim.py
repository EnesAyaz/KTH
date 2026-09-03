import argparse
import json
import shutil
from pathlib import Path


# =========================================================
# PROJECT PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

DATA_DIR = (
    ROOT_DIR
    / "data"
)

BACKUP_DIR = (
    DATA_DIR
    / "backups"
)

EVIDENCE_FILE = (
    DATA_DIR
    / "evidence.json"
)


BACKUP_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# LOAD JSON
# =========================================================

def load_database():

    if not EVIDENCE_FILE.exists():

        raise FileNotFoundError(
            f"Could not find:\n"
            f"{EVIDENCE_FILE}"
        )

    return json.loads(
        EVIDENCE_FILE.read_text(
            encoding="utf-8"
        )
    )


# =========================================================
# FIND PAPER
# =========================================================

def find_paper(
    database,
    citation_key,
):

    matches = [

        paper

        for paper in database.get(
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

    if len(matches) == 0:

        raise RuntimeError(
            f"No evidence entry found for "
            f"{citation_key}."
        )

    if len(matches) > 1:

        raise RuntimeError(
            f"Multiple evidence entries found for "
            f"{citation_key}."
        )

    return matches[0]


# =========================================================
# BACKUP
# =========================================================

def create_backup(
    citation_key,
    claim_id,
):

    safe_claim_id = (
        claim_id
        .replace(
            "/",
            "_"
        )
        .replace(
            "\\",
            "_"
        )
    )

    backup_file = (
        BACKUP_DIR
        / (
            f"evidence_before_removing_"
            f"{safe_claim_id}.json"
        )
    )

    shutil.copy2(
        EVIDENCE_FILE,
        backup_file,
    )

    return backup_file


# =========================================================
# RENUMBER CLAIMS
# =========================================================

def renumber_claims(
    paper,
):

    citation_key = (
        paper[
            "citation_key"
        ]
    )

    claims = paper.get(
        "claims",
        []
    )

    changes = []

    for index, claim in enumerate(
        claims,
        start=1,
    ):

        old_id = claim.get(
            "claim_id"
        )

        new_id = (
            f"{citation_key}_C"
            f"{index:02d}"
        )

        claim[
            "claim_id"
        ] = new_id

        claim[
            "citation_key"
        ] = citation_key

        if old_id != new_id:

            changes.append(
                (
                    old_id,
                    new_id,
                )
            )

    return changes


# =========================================================
# REMOVE CLAIM
# =========================================================

def remove_claim(
    paper,
    claim_id,
):

    claims = paper.get(
        "claims",
        []
    )

    matching = [

        claim

        for claim in claims

        if (
            claim.get(
                "claim_id"
            )
            == claim_id
        )
    ]

    if len(matching) == 0:

        raise RuntimeError(
            f"Claim not found: "
            f"{claim_id}"
        )

    if len(matching) > 1:

        raise RuntimeError(
            f"Multiple claims found with ID "
            f"{claim_id}."
        )

    removed_claim = (
        matching[0]
    )

    paper[
        "claims"
    ] = [

        claim

        for claim in claims

        if (
            claim.get(
                "claim_id"
            )
            != claim_id
        )
    ]

    return removed_claim


# =========================================================
# MAIN
# =========================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Safely remove one scientific evidence claim "
            "and renumber the remaining claims."
        )
    )

    parser.add_argument(
        "--key",
        required=True,
        help=(
            "Paper citation key, for example "
            "Verkroost2024a."
        ),
    )

    parser.add_argument(
        "--claim",
        required=True,
        help=(
            "Claim ID to remove, for example "
            "Verkroost2024a_C17."
        ),
    )

    args = parser.parse_args()

    citation_key = (
        args.key
    )

    claim_id = (
        args.claim
    )

    print()
    print(
        "========================================"
    )

    print(
        "REMOVE EVIDENCE CLAIM"
    )

    print(
        "========================================"
    )

    print()

    # -----------------------------------------------------
    # LOAD
    # -----------------------------------------------------

    try:

        database = (
            load_database()
        )

        paper = (
            find_paper(
                database,
                citation_key,
            )
        )

    except Exception as error:

        print(
            "ERROR:"
        )

        print(error)

        return

    # -----------------------------------------------------
    # DISPLAY CLAIM BEFORE REMOVAL
    # -----------------------------------------------------

    matches = [

        claim

        for claim in paper.get(
            "claims",
            []
        )

        if (
            claim.get(
                "claim_id"
            )
            == claim_id
        )
    ]

    if not matches:

        print(
            f"Claim not found:"
        )

        print(
            claim_id
        )

        return

    claim = (
        matches[0]
    )

    print(
        "Claim to remove:"
    )

    print()

    print(
        f"ID:"
    )

    print(
        claim.get(
            "claim_id"
        )
    )

    print()

    print(
        "Statement:"
    )

    print(
        claim.get(
            "statement"
        )
    )

    print()

    # -----------------------------------------------------
    # BACKUP
    # -----------------------------------------------------

    backup_file = (
        create_backup(
            citation_key,
            claim_id,
        )
    )

    print(
        "Backup created:"
    )

    print(
        backup_file
    )

    print()

    # -----------------------------------------------------
    # REMOVE
    # -----------------------------------------------------

    try:

        removed_claim = (
            remove_claim(
                paper,
                claim_id,
            )
        )

    except Exception as error:

        print(
            "ERROR:"
        )

        print(error)

        return

    # -----------------------------------------------------
    # RENUMBER
    # -----------------------------------------------------

    changes = (
        renumber_claims(
            paper
        )
    )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    EVIDENCE_FILE.write_text(
        json.dumps(
            database,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # REPORT
    # -----------------------------------------------------

    print(
        "========================================"
    )

    print(
        "CLAIM REMOVED"
    )

    print(
        "========================================"
    )

    print()

    print(
        f"Removed:"
    )

    print(
        removed_claim.get(
            "claim_id"
        )
    )

    print()

    print(
        f"Remaining claims:"
    )

    print(
        len(
            paper.get(
                "claims",
                []
            )
        )
    )

    print()

    if changes:

        print(
            "Renumbered claims:"
        )

        print()

        for (
            old_id,
            new_id,
        ) in changes:

            print(
                f"{old_id} -> {new_id}"
            )

        print()

    else:

        print(
            "No subsequent claim IDs required "
            "renumbering."
        )

        print()

    print(
        "Updated evidence database:"
    )

    print(
        EVIDENCE_FILE
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()