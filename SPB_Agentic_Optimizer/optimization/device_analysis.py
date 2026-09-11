import pandas as pd

from models.fom import (
    calculate_device_foms,
)


def build_device_fom_table(
    devices,
):
    """
    Build semiconductor FOM comparison table.
    """

    records = []

    for device in devices:

        foms = (
            calculate_device_foms(
                device
            )
        )

        record = {

            "manufacturer":
                device.manufacturer,

            "device":
                device.part_number,

            "voltage_rating_v":
                device.vds_rating,

            "continuous_current_a":
                device.id_continuous,

            "rds_on_25c_mohm":
                device.rds_on_25c
                * 1e3,

            "qg_nc":
                device.qg
                * 1e9,

            "qgd_nc":
                device.qgd
                * 1e9,

            "coss_pf":
                device.coss
                * 1e12,

            "eoss_uj":
                (
                    device.eoss
                    * 1e6
                    if device.eoss is not None
                    else None
                ),

            "fom_rds_qg_mohm_nc":
                foms[
                    "fom_rds_qg_mohm_nc"
                ],

            "fom_rds_qgd_mohm_nc":
                foms[
                    "fom_rds_qgd_mohm_nc"
                ],

            "fom_rds_coss_mohm_pf":
                foms[
                    "fom_rds_coss_mohm_pf"
                ],

            "fom_rds_eoss_mohm_uj":
                foms[
                    "fom_rds_eoss_mohm_uj"
                ],

            "fom_rds_qg_confidence":
                foms[
                    "fom_rds_qg_confidence"
                ],

            "fom_rds_qgd_confidence":
                foms[
                    "fom_rds_qgd_confidence"
                ],

            "fom_rds_coss_confidence":
                foms[
                    "fom_rds_coss_confidence"
                ],

            "fom_rds_eoss_confidence":
                foms[
                    "fom_rds_eoss_confidence"
                ],

            "fom_notes":
                foms[
                    "fom_notes"
                ],
        }

        records.append(
            record
        )

    df = pd.DataFrame(
        records
    )

    # ==================================================
    # RANKS
    #
    # Lower FOM is better.
    # ==================================================

    df[
        "rank_rds_qg"
    ] = (

        df[
            "fom_rds_qg_mohm_nc"
        ]

        .rank(
            method="min",
            ascending=True,
        )
    )

    df[
        "rank_rds_qgd"
    ] = (

        df[
            "fom_rds_qgd_mohm_nc"
        ]

        .rank(
            method="min",
            ascending=True,
        )
    )

    df[
        "rank_rds_coss"
    ] = (

        df[
            "fom_rds_coss_mohm_pf"
        ]

        .rank(
            method="min",
            ascending=True,
        )
    )

    # ==================================================
    # NORMALIZED FOM SCORE
    #
    # This is only a screening score.
    #
    # 50% RdsQg
    # 30% RdsQgd
    # 20% RdsCoss
    # ==================================================

    columns = [

        "fom_rds_qg_mohm_nc",

        "fom_rds_qgd_mohm_nc",

        "fom_rds_coss_mohm_pf",
    ]

    score_columns = []

    for column in columns:

        minimum = (
            df[
                column
            ].min()
        )

        maximum = (
            df[
                column
            ].max()
        )

        score_column = (
            column
            + "_score"
        )

        if maximum == minimum:

            df[
                score_column
            ] = 1.0

        else:

            df[
                score_column
            ] = (

                1.0

                -

                (
                    df[
                        column
                    ]
                    - minimum
                )

                /

                (
                    maximum
                    - minimum
                )
            )

        score_columns.append(
            score_column
        )

    df[
        "device_fom_screening_score"
    ] = (

        0.50
        * df[
            score_columns[0]
        ]

        +

        0.30
        * df[
            score_columns[1]
        ]

        +

        0.20
        * df[
            score_columns[2]
        ]
    )

    df[
        "device_fom_screening_score_percent"
    ] = (

        df[
            "device_fom_screening_score"
        ]

        * 100.0
    )

    df[
        "overall_fom_rank"
    ] = (

        df[
            "device_fom_screening_score"
        ]

        .rank(
            method="min",
            ascending=False,
        )
    )

    return (

        df

        .sort_values(
            "overall_fom_rank"
        )

        .reset_index(
            drop=True
        )
    )