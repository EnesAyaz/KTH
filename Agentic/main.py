import asyncio
from pathlib import Path

from dotenv import load_dotenv
from agents import Runner

from paper_agents.planner import planner_agent


load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


async def main():

    print("\n==============================")
    print("STEP 1: PLANNING REVIEW PAPER")
    print("==============================\n")

    result = await Runner.run(
        planner_agent,
        """
Create a detailed review-paper structure based on
the supplied paper scope.
"""
    )

    outline = result.final_output

    print(outline)

    outline_file = OUTPUT_DIR / "outline.md"

    outline_file.write_text(
        str(outline),
        encoding="utf-8"
    )

    print("\nOutline saved to:")
    print(outline_file)


if __name__ == "__main__":
    asyncio.run(main())