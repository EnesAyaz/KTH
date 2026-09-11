from pathlib import Path

import pandas as pd


# ==========================================================
# HELPERS
# ==========================================================

def _read_optional_sheet(
    filename,
    sheet_name,
):
    """
    Read an Excel sheet if it exists.

    Missing workbook or sheet returns an empty DataFrame.

    This allows the optimizer to continue working before
    real curve data are available.
    """

    path = Path(
        filename
    )

    if not path.exists():

        return pd.DataFrame()

    try:

        return pd.read_excel(
            path,
            sheet_name=sheet_name,
        )

    except ValueError:

        return pd.DataFrame()


# ==========================================================
# RDS TEMPERATURE CURVE
# ==========================================================

def load_rds_temperature_curves(
    filename="database/device_curves.xlsx",
):
    """
    Expected sheet:

        Rds_Temperature

    Columns:

        part_number
        temperature_c
        rds_multiplier
        source
        confidence

    Example:

        EPC2304 | 25  | 1.00
        EPC2304 | 75  | 1.25
        EPC2304 | 125 | 1.55
    """

    df = _read_optional_sheet(
        filename,
        "Rds_Temperature",
    )

    if df.empty:
        return {}

    required = [
        "part_number",
        "temperature_c",
        "rds_multiplier",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing columns in Rds_Temperature sheet: "
            + ", ".join(
                missing
            )
        )

    curves = {}

    for part_number, group in (
        df.groupby(
            "part_number"
        )
    ):

        group = (
            group
            .sort_values(
                "temperature_c"
            )
        )

        points = []

        for _, row in (
            group.iterrows()
        ):

            points.append(
                {
                    "temperature_c":
                        float(
                            row[
                                "temperature_c"
                            ]
                        ),

                    "rds_multiplier":
                        float(
                            row[
                                "rds_multiplier"
                            ]
                        ),

                    "source":
                        (
                            str(
                                row[
                                    "source"
                                ]
                            )
                            if (
                                "source"
                                in row.index
                                and
                                pd.notna(
                                    row[
                                        "source"
                                    ]
                                )
                            )
                            else None
                        ),

                    "confidence":
                        (
                            str(
                                row[
                                    "confidence"
                                ]
                            )
                            if (
                                "confidence"
                                in row.index
                                and
                                pd.notna(
                                    row[
                                        "confidence"
                                    ]
                                )
                            )
                            else "medium"
                        ),
                }
            )

        curves[
            str(
                part_number
            )
        ] = points

    return curves


# ==========================================================
# EOSS CURVE
# ==========================================================

def load_eoss_curves(
    filename="database/device_curves.xlsx",
):
    """
    Expected sheet:

        Eoss

    Columns:

        part_number
        voltage_v
        eoss_uj
        source
        confidence
    """

    df = _read_optional_sheet(
        filename,
        "Eoss",
    )

    if df.empty:
        return {}

    required = [
        "part_number",
        "voltage_v",
        "eoss_uj",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing columns in Eoss sheet: "
            + ", ".join(
                missing
            )
        )

    curves = {}

    for part_number, group in (
        df.groupby(
            "part_number"
        )
    ):

        group = (
            group
            .sort_values(
                "voltage_v"
            )
        )

        points = []

        for _, row in (
            group.iterrows()
        ):

            points.append(
                {
                    "voltage_v":
                        float(
                            row[
                                "voltage_v"
                            ]
                        ),

                    "eoss_j":
                        float(
                            row[
                                "eoss_uj"
                            ]
                        )
                        * 1e-6,

                    "source":
                        (
                            str(
                                row[
                                    "source"
                                ]
                            )
                            if (
                                "source"
                                in row.index
                                and
                                pd.notna(
                                    row[
                                        "source"
                                    ]
                                )
                            )
                            else None
                        ),

                    "confidence":
                        (
                            str(
                                row[
                                    "confidence"
                                ]
                            )
                            if (
                                "confidence"
                                in row.index
                                and
                                pd.notna(
                                    row[
                                        "confidence"
                                    ]
                                )
                            )
                            else "medium"
                        ),
                }
            )

        curves[
            str(
                part_number
            )
        ] = points

    return curves


# ==========================================================
# QOSS CURVE
# ==========================================================

def load_qoss_curves(
    filename="database/device_curves.xlsx",
):
    """
    Expected sheet:

        Qoss

    Columns:

        part_number
        voltage_v
        qoss_nc
        source
        confidence
    """

    df = _read_optional_sheet(
        filename,
        "Qoss",
    )

    if df.empty:
        return {}

    required = [
        "part_number",
        "voltage_v",
        "qoss_nc",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing columns in Qoss sheet: "
            + ", ".join(
                missing
            )
        )

    curves = {}

    for part_number, group in (
        df.groupby(
            "part_number"
        )
    ):

        group = (
            group
            .sort_values(
                "voltage_v"
            )
        )

        points = []

        for _, row in (
            group.iterrows()
        ):

            points.append(
                {
                    "voltage_v":
                        float(
                            row[
                                "voltage_v"
                            ]
                        ),

                    "qoss_c":
                        float(
                            row[
                                "qoss_nc"
                            ]
                        )
                        * 1e-9,

                    "source":
                        (
                            str(
                                row[
                                    "source"
                                ]
                            )
                            if (
                                "source"
                                in row.index
                                and
                                pd.notna(
                                    row[
                                        "source"
                                    ]
                                )
                            )
                            else None
                        ),

                    "confidence":
                        (
                            str(
                                row[
                                    "confidence"
                                ]
                            )
                            if (
                                "confidence"
                                in row.index
                                and
                                pd.notna(
                                    row[
                                        "confidence"
                                    ]
                                )
                            )
                            else "medium"
                        ),
                }
            )

        curves[
            str(
                part_number
            )
        ] = points

    return curves


# ==========================================================
# SWITCHING ENERGY CURVE
# ==========================================================

def load_switching_energy_curves(
    filename="database/device_curves.xlsx",
):
    """
    Expected sheet:

        Switching_Energy

    Columns:

        part_number
        voltage_v
        current_a
        eon_uj
        eoff_uj
        rg_ohm
        temperature_c
        source
        confidence

    Multiple current points at a given voltage are allowed.
    """

    df = _read_optional_sheet(
        filename,
        "Switching_Energy",
    )

    if df.empty:
        return {}

    required = [
        "part_number",
        "voltage_v",
        "current_a",
        "eon_uj",
        "eoff_uj",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing columns in Switching_Energy sheet: "
            + ", ".join(
                missing
            )
        )

    curves = {}

    for part_number, group in (
        df.groupby(
            "part_number"
        )
    ):

        points = []

        for _, row in (
            group.iterrows()
        ):

            points.append(
                {
                    "voltage_v":
                        float(
                            row[
                                "voltage_v"
                            ]
                        ),

                    "current_a":
                        float(
                            row[
                                "current_a"
                            ]
                        ),

                    "eon_j":
                        float(
                            row[
                                "eon_uj"
                            ]
                        )
                        * 1e-6,

                    "eoff_j":
                        float(
                            row[
                                "eoff_uj"
                            ]
                        )
                        * 1e-6,

                    "rg_ohm":
                        (
                            float(
                                row[
                                    "rg_ohm"
                                ]
                            )
                            if (
                                "rg_ohm"
                                in row.index
                                and
                                pd.notna(
                                    row[
                                        "rg_ohm"
                                    ]
                                )
                            )
                            else None
                        ),

                    "temperature_c":
                        (
                            float(
                                row[
                                    "temperature_c"
                                ]
                            )
                            if (
                                "temperature_c"
                                in row.index
                                and
                                pd.notna(
                                    row[
                                        "temperature_c"
                                    ]
                                )
                            )
                            else None
                        ),

                    "source":
                        (
                            str(
                                row[
                                    "source"
                                ]
                            )
                            if (
                                "source"
                                in row.index
                                and
                                pd.notna(
                                    row[
                                        "source"
                                    ]
                                )
                            )
                            else None
                        ),

                    "confidence":
                        (
                            str(
                                row[
                                    "confidence"
                                ]
                            )
                            if (
                                "confidence"
                                in row.index
                                and
                                pd.notna(
                                    row[
                                        "confidence"
                                    ]
                                )
                            )
                            else "medium"
                        ),
                }
            )

        curves[
            str(
                part_number
            )
        ] = points

    return curves


# ==========================================================
# LOAD EVERYTHING
# ==========================================================

def load_all_device_curves(
    filename="database/device_curves.xlsx",
):
    """
    Return one dictionary containing all available
    semiconductor curve data.
    """

    return {

        "rds_temperature":
            load_rds_temperature_curves(
                filename
            ),

        "eoss":
            load_eoss_curves(
                filename
            ),

        "qoss":
            load_qoss_curves(
                filename
            ),

        "switching_energy":
            load_switching_energy_curves(
                filename
            ),
    }