from pathlib import Path

from agents import Agent


ROOT_DIR = Path(__file__).resolve().parents[1]

PAPER_SCOPE = (
    ROOT_DIR / "prompts" / "paper_scope.txt"
).read_text(encoding="utf-8")


planner_agent = Agent(
    name="Review Paper Planner",

    instructions=f"""
You are a senior academic researcher specializing in
power electronics and electric drives.

Your task is to develop the structure of a rigorous
engineering review paper.

Here is the scope of the paper:

--------------------------------
PAPER SCOPE
--------------------------------

{PAPER_SCOPE}

--------------------------------

Your responsibilities are to determine:

- the central research question
- appropriate review taxonomy
- major sections
- subsections
- important comparison dimensions
- required tables
- required figures
- research gaps that should be investigated
- questions that the literature review must answer

Do NOT write the actual paper yet.

Do NOT invent references.

Return a detailed hierarchical paper outline.
"""
)