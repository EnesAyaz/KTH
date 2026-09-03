import json
import shutil
import subprocess
from pathlib import Path


# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent

FIGURE_PLAN_FILE = (
    ROOT_DIR
    / "data"
    / "figure_plan.json"
)

MATLAB_DIR = (
    ROOT_DIR
    / "figures"
    / "matlab"
)

GENERATED_DIR = (
    ROOT_DIR
    / "figures"
    / "generated"
)


# =========================================================
# RUN MATLAB SCRIPT
# =========================================================

def run_matlab_script(
    script_path
):

    script_stem = (
        script_path.stem
    )

    matlab_directory = (
        str(
            MATLAB_DIR.resolve()
        )
        .replace(
            "\\",
            "/"
        )
        .replace(
            "'",
            "''"
        )
    )

    matlab_command = (
        f"cd('{matlab_directory}'); "
        f"{script_stem};"
    )

    print()
    print(
        f"Running MATLAB:"
    )

    print(
        script_path.name
    )

    result = subprocess.run(
        [
            "matlab",
            "-batch",
            matlab_command,
        ],
        text=True,
    )

    return (
        result.returncode
        == 0
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
        "RUNNING MATLAB FIGURES"
    )

    print(
        "========================================"
    )

    print()

    matlab_path = (
        shutil.which(
            "matlab"
        )
    )

    if matlab_path is None:

        print(
            "MATLAB was not found in PATH."
        )

        print()
        print(
            "You can still open the scripts manually from:"
        )

        print()
        print(
            MATLAB_DIR
        )

        return

    print(
        f"MATLAB found:"
    )

    print(
        matlab_path
    )

    if not FIGURE_PLAN_FILE.exists():

        print(
            "figure_plan.json not found."
        )

        return

    plan = json.loads(
        FIGURE_PLAN_FILE.read_text(
            encoding="utf-8"
        )
    )

    figures = plan.get(
        "figures",
        []
    )

    successful = 0
    failed = 0

    for figure in figures:

        script_file = (
            MATLAB_DIR
            / figure[
                "matlab_filename"
            ]
        )

        if not script_file.exists():

            print(
                f"Missing MATLAB script: "
                f"{script_file}"
            )

            failed += 1

            continue

        success = (
            run_matlab_script(
                script_file
            )
        )

        if success:

            successful += 1

        else:

            failed += 1

    print()
    print(
        "========================================"
    )

    print(
        "MATLAB FIGURE SUMMARY"
    )

    print(
        "========================================"
    )

    print()

    print(
        f"Successful: {successful}"
    )

    print(
        f"Failed:     {failed}"
    )

    print()

    print(
        f"Figures directory:"
    )

    print(
        GENERATED_DIR
    )

    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()