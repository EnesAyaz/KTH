import os

import pandas as pd


def main():

    os.makedirs(
        "database",
        exist_ok=True,
    )

    filename = (
        "database/device_curves.xlsx"
    )

    # ======================================================
    # RDS TEMPERATURE
    # ======================================================

    rds_temperature = pd.DataFrame(
        columns=[
            "part_number",
            "temperature_c",
            "rds_multiplier",
            "source",
            "confidence",
        ]
    )

    # ======================================================
    # EOSS
    # ======================================================

    eoss = pd.DataFrame(
        columns=[
            "part_number",
            "voltage_v",
            "eoss_uj",
            "source",
            "confidence",
        ]
    )

    # ======================================================
    # QOSS
    # ======================================================

    qoss = pd.DataFrame(
        columns=[
            "part_number",
            "voltage_v",
            "qoss_nc",
            "source",
            "confidence",
        ]
    )

    # ======================================================
    # SWITCHING ENERGY
    # ======================================================

    switching_energy = pd.DataFrame(
        columns=[
            "part_number",
            "voltage_v",
            "current_a",
            "eon_uj",
            "eoff_uj",
            "rg_ohm",
            "temperature_c",
            "source",
            "confidence",
        ]
    )

    with pd.ExcelWriter(
        filename,
        engine="openpyxl",
    ) as writer:

        rds_temperature.to_excel(
            writer,
            sheet_name="Rds_Temperature",
            index=False,
        )

        eoss.to_excel(
            writer,
            sheet_name="Eoss",
            index=False,
        )

        qoss.to_excel(
            writer,
            sheet_name="Qoss",
            index=False,
        )

        switching_energy.to_excel(
            writer,
            sheet_name="Switching_Energy",
            index=False,
        )

    print(
        "\nCurve database template created:"
    )

    print(
        f"    {filename}"
    )


if __name__ == "__main__":

    main()