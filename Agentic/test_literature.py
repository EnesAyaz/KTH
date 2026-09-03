import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
from agents import Runner

from paper_agents.literature import literature_agent


load_dotenv()


ROOT_DIR = Path(__file__).resolve().parent

PAPERS_FILE = (
    ROOT_DIR /
    "data" /
    "papers.json"
)


async def main():

    result = await Runner.run(
        literature_agent,
        """
Find five important peer-reviewed publications related to:

stacked polyphase bridge converters,
multiphase traction drives,
and integrated modular motor drives.

Verify bibliographic metadata.

Do not invent missing information.
"""
    )

    database = result.final_output

    data = database.model_dump()

    PAPERS_FILE.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("\nLiterature search complete.")
    print(f"Saved to: {PAPERS_FILE}")


if __name__ == "__main__":
    asyncio.run(main())