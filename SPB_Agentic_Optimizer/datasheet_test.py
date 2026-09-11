import sys

from agents.datasheet_agent import (
    DatasheetAgent,
)


def main():

    if len(
        sys.argv
    ) < 2:

        print(
            """
Usage:

python datasheet_test.py <datasheet.pdf>

Example:

python datasheet_test.py database/datasheets/EPC2304.pdf
"""
        )

        return

    pdf_path = (
        sys.argv[1]
    )

    manufacturer = None

    if len(
        sys.argv
    ) >= 3:

        manufacturer = (
            sys.argv[2]
        )

    agent = DatasheetAgent()

    agent.extract_device(
        pdf_path=pdf_path,
        manufacturer=manufacturer,
    )


if __name__ == "__main__":

    main()