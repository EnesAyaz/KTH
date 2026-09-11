import pandas as pd

from models.semiconductor import (
    GaNDevice,
)

from database.curve_loader import (
    load_all_device_curves,
)


def optional_float(
    value,
    scale=1.0,
):
    if pd.isna(
        value
    ):
        return None

    return (
        float(
            value
        )
        * scale
    )


def load_gan_devices(
    filename="database/gan_devices.xlsx",
    curve_filename="database/device_curves.xlsx",
):
    """
    Load semiconductor scalar data and optional
    datasheet curve data.
    """

    df = pd.read_excel(
        filename,
        sheet_name="GaN_Devices",
    )

    required_columns = [

        "manufacturer",

        "part_number",

        "vds_rating",

        "id_continuous",

        "rds_on_25c_mohm",

        "rds_temp_factor_125c",

        "qg_nc",

        "qgd_nc",

        "coss_pf",

        "eoss_uj",

        "eon_uj",

        "eoff_uj",

        "eon_test_voltage",

        "eon_test_current",

        "rth_jc",

        "price",

        "package_area_mm2",
    ]

    missing_columns = [

        column

        for column
        in required_columns

        if column
        not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing columns in GaN database: "
            + ", ".join(
                missing_columns
            )
        )

    # ======================================================
    # CURVES
    # ======================================================

    curves = (
        load_all_device_curves(
            curve_filename
        )
    )

    devices = []

    for _, row in (
        df.iterrows()
    ):

        part_number = str(
            row[
                "part_number"
            ]
        )

        device = GaNDevice(

            manufacturer=str(
                row[
                    "manufacturer"
                ]
            ),

            part_number=part_number,

            vds_rating=float(
                row[
                    "vds_rating"
                ]
            ),

            id_continuous=float(
                row[
                    "id_continuous"
                ]
            ),

            rds_on_25c=(
                float(
                    row[
                        "rds_on_25c_mohm"
                    ]
                )
                * 1e-3
            ),

            rds_temp_factor_125c=(
                optional_float(
                    row[
                        "rds_temp_factor_125c"
                    ]
                )
            ),

            qg=(
                optional_float(
                    row[
                        "qg_nc"
                    ],
                    1e-9,
                )
            ),

            qgd=(
                optional_float(
                    row[
                        "qgd_nc"
                    ],
                    1e-9,
                )
            ),

            coss=(
                optional_float(
                    row[
                        "coss_pf"
                    ],
                    1e-12,
                )
            ),

            eoss=(
                optional_float(
                    row[
                        "eoss_uj"
                    ],
                    1e-6,
                )
            ),

            eon=(
                optional_float(
                    row[
                        "eon_uj"
                    ],
                    1e-6,
                )
            ),

            eoff=(
                optional_float(
                    row[
                        "eoff_uj"
                    ],
                    1e-6,
                )
            ),

            eon_test_voltage=(
                optional_float(
                    row[
                        "eon_test_voltage"
                    ]
                )
            ),

            eon_test_current=(
                optional_float(
                    row[
                        "eon_test_current"
                    ]
                )
            ),

            rth_jc=float(
                row[
                    "rth_jc"
                ]
            ),

            price=float(
                row[
                    "price"
                ]
            ),

            package_area_mm2=float(
                row[
                    "package_area_mm2"
                ]
            ),

            # ==============================================
            # CURVES
            # ==============================================

            rds_temperature_curve=(
                curves[
                    "rds_temperature"
                ].get(
                    part_number,
                    [],
                )
            ),

            eoss_curve=(
                curves[
                    "eoss"
                ].get(
                    part_number,
                    [],
                )
            ),

            qoss_curve=(
                curves[
                    "qoss"
                ].get(
                    part_number,
                    [],
                )
            ),

            switching_energy_curve=(
                curves[
                    "switching_energy"
                ].get(
                    part_number,
                    [],
                )
            ),
        )

        devices.append(
            device
        )

    return devices