import os

import matplotlib.pyplot as plt

from optimization.device_analysis import (
    build_device_fom_table,
)


def generate_device_fom_report(
    devices,
    output_folder="results",
):
    """
    Generate semiconductor FOM tables and plots.
    """

    os.makedirs(
        output_folder,
        exist_ok=True,
    )

    df = (
        build_device_fom_table(
            devices
        )
    )

    # ==================================================
    # EXCEL
    # ==================================================

    filename = (
        output_folder
        + "/device_fom_analysis.xlsx"
    )

    df.to_excel(
        filename,
        index=False,
    )

    # ==================================================
    # TERMINAL
    # ==================================================

    print("\n")
    print("=" * 120)
    print("SEMICONDUCTOR FOM ANALYSIS")
    print("=" * 120)

    print()

    print(
        df[
            [
                "device",
                "voltage_rating_v",
                "rds_on_25c_mohm",
                "qg_nc",
                "qgd_nc",
                "fom_rds_qg_mohm_nc",
                "fom_rds_qgd_mohm_nc",
                "device_fom_screening_score_percent",
                "overall_fom_rank",
            ]
        ]
        .round(
            3
        )
        .to_string(
            index=False
        )
    )

    print()

    print(
        "NOTE:"
    )

    print(
        "The FOM ranking is currently a screening tool, "
        "not the final converter ranking."
    )

    print(
        "The converter optimizer still calculates actual "
        "conduction, switching, thermal, auxiliary and "
        "machine-system performance."
    )

    # ==================================================
    # RDS QG PLOT
    # ==================================================

    plt.figure(
        figsize=(10, 6)
    )

    plt.scatter(
        df[
            "voltage_rating_v"
        ],
        df[
            "fom_rds_qg_mohm_nc"
        ],
    )

    for _, row in (
        df.iterrows()
    ):

        plt.annotate(
            row[
                "device"
            ],
            (
                row[
                    "voltage_rating_v"
                ],
                row[
                    "fom_rds_qg_mohm_nc"
                ],
            ),
        )

    plt.xlabel(
        "Device Voltage Rating [V]"
    )

    plt.ylabel(
        "Rds(on) × Qg [mOhm nC]"
    )

    plt.title(
        "GaN Device FOM: Rds(on) × Qg"
    )

    plt.grid(
        True
    )

    plt.tight_layout()

    plt.savefig(
        output_folder
        + "/device_fom_rds_qg.png",
        dpi=300,
    )

    plt.show()

    # ==================================================
    # RDS QGD PLOT
    # ==================================================

    plt.figure(
        figsize=(10, 6)
    )

    plt.scatter(
        df[
            "voltage_rating_v"
        ],
        df[
            "fom_rds_qgd_mohm_nc"
        ],
    )

    for _, row in (
        df.iterrows()
    ):

        plt.annotate(
            row[
                "device"
            ],
            (
                row[
                    "voltage_rating_v"
                ],
                row[
                    "fom_rds_qgd_mohm_nc"
                ],
            ),
        )

    plt.xlabel(
        "Device Voltage Rating [V]"
    )

    plt.ylabel(
        "Rds(on) × Qgd [mOhm nC]"
    )

    plt.title(
        "GaN Switching FOM: Rds(on) × Qgd"
    )

    plt.grid(
        True
    )

    plt.tight_layout()

    plt.savefig(
        output_folder
        + "/device_fom_rds_qgd.png",
        dpi=300,
    )

    plt.show()

    return df