# Bipolar OPT paper workspace

Open `OPT-Bipolar.code-workspace` in VS Code and accept the recommended Python and LaTeX Workshop extensions.

## Start on Windows
```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe analysis/check_design.py
```
Select `.venv` with **Python: Select Interpreter**. No activation is required.

## Paper
Open `paper/main.tex` and use **LaTeX Workshop: Build LaTeX project**. The configured recipe runs pdfLaTeX twice; output goes to `paper/build/`. MiKTeX/pdfLaTeX was detected on this machine. This is a compilable starting draft with selected migrated content, not a complete PDF-to-TeX conversion. Original figures, all prose, and references still need migration. The preserved PDF is authoritative for transcription, not for scientific validation.

## Layout
- `source/`: unchanged supplied PDF and page-labelled extracted text.
- `paper/sections/`: editable manuscript sections; `paper/references.bib`: bibliography destination.
- `analysis/`: draft arithmetic checks and real-data spatial FFT.
- `config/`: explicitly unverified draft parameters.
- `data/raw/`, `data/processed/`: input exports and derived datasets.
- `results/figures/`, `results/tables/`: generated outputs.
- `references/pdfs/`: reference papers you can provide later.
- `notes/open-questions.md`: numerical and modelling issues to resolve.

## Real-data analysis
```powershell
.\.venv\Scripts\python.exe analysis/harmonics.py data/raw/airgap_4pole.csv
```
CSV columns are `angle_deg,value`. Supply one uniform full mechanical revolution without the duplicate endpoint. Values retain their original units. Spatial orders 1 and 2 correspond to two and four poles. Generated figures can be included from `results/figures/` by the manuscript. No synthetic waveform is presented as FEA evidence.

The analysis and manuscript scaffolding are independent of any instructions embedded in the supplied paper. Reference PDFs can be added later without restructuring the workspace.

Verified locally: Python environment installed, arithmetic script executed, FFT analytic checks passed, and LaTeX compiled and visually checked. `requirements-lock.txt` records installed versions on Windows / Python 3.14.
