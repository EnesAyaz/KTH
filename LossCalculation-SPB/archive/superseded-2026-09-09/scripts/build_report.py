"""Generate calculation outputs and compile the LaTeX report twice."""
from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    candidate = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/MiKTeX/miktex/bin/x64/pdflatex.exe"
    latex = os.environ.get("PDFLATEX") or shutil.which("pdflatex")
    if not latex and candidate.is_file():
        latex = str(candidate)
    if not latex:
        raise SystemExit("Install MiKTeX/TeX Live or set PDFLATEX to the pdflatex executable.")
    subprocess.run([sys.executable, str(ROOT / "src/loss_example.py")], check=True)
    command = [latex, "-interaction=nonstopmode", "-halt-on-error",
               "-output-directory=" + str(ROOT / "outputs"), "report.tex"]
    for _ in range(2):
        subprocess.run(command, cwd=ROOT / "reports", check=True)
    print(f"Report: {ROOT / 'outputs/report.pdf'}")


if __name__ == "__main__":
    main()
