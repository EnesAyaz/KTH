import pandas as pd

from models.converter import (
    evaluate_design,
)

from optimization.design_space import (
    generate_design_space,
)

from optimization.objectives import (
    calculate_constraint_metrics,
    is_fully_feasible,
)

from optimization.device_analysis import (
    build_device_fom_table,
)


def run_full_design_space(
    config,
    devices,
):
    """
    Evaluate complete discrete SPB design space:

        device
        x
        cell count
        x
        switching frequency
        x
        parallel-device count

    Quantitative semiconductor FOM data are attached
    to every result.
    """

    results = []

    evaluated_count = 0

    # ==================================================
    # DEVICE FOM DATABASE
    # ==================================================

    fom_df = (
        build_device_fom_table(
            devices
        )
    )

    fom_lookup = {}

    for _, row in (
        fom_df.iterrows()
    ):

        fom_lookup[
            row[
                "device"
            ]
        ] = row.to_dict()

    # ==================================================
    # FULL DESIGN SEARCH
    # ==================================================

    for candidate in generate_design_space(
        config=config,
        devices=devices,
    ):

        evaluated_count += 1

        result = evaluate_design(

            config=config,

            device=candidate[
                "device"
            ],

            n_cells=candidate[
                "cells"
            ],

            fsw=candidate[
                "fsw"
            ],

            parallel_devices_override=(
                candidate[
                    "parallel_devices"
                ]
            ),
        )

        if result is None:

            continue

        # ==================================================
        # CONSTRAINT METRICS
        # ==================================================

        metrics = (
            calculate_constraint_metrics(
                result=result,
                config=config,
            )
        )

        result.update(
            metrics
        )

        # ==================================================
        # HARD CONSTRAINT STATUS
        # ==================================================

        result[
            "fully_feasible"
        ] = (
            is_fully_feasible(
                result
            )
        )

        # ==================================================
        # ATTACH DEVICE FOM
        # ==================================================

        device_name = (
            result[
                "device"
            ]
        )

        if device_name in fom_lookup:

            fom_record = (
                fom_lookup[
                    device_name
                ]
            )

            result[
                "fom_rds_qg_mohm_nc"
            ] = (
                fom_record[
                    "fom_rds_qg_mohm_nc"
                ]
            )

            result[
                "fom_rds_qgd_mohm_nc"
            ] = (
                fom_record[
                    "fom_rds_qgd_mohm_nc"
                ]
            )

            result[
                "fom_rds_coss_mohm_pf"
            ] = (
                fom_record[
                    "fom_rds_coss_mohm_pf"
                ]
            )

            result[
                "fom_rds_eoss_mohm_uj"
            ] = (
                fom_record[
                    "fom_rds_eoss_mohm_uj"
                ]
            )

            result[
                "device_fom_screening_score_percent"
            ] = (
                fom_record[
                    "device_fom_screening_score_percent"
                ]
            )

            result[
                "overall_fom_rank"
            ] = (
                fom_record[
                    "overall_fom_rank"
                ]
            )

        results.append(
            result
        )

    df = pd.DataFrame(
        results
    )

    return (
        df,
        evaluated_count,
    )


def get_fully_feasible_designs(
    df,
):

    if df.empty:

        return pd.DataFrame()

    return (

        df[
            df[
                "fully_feasible"
            ]
        ]

        .copy()

        .reset_index(
            drop=True
        )
    )


def find_system_sweet_point(
    df,
):

    feasible = (
        get_fully_feasible_designs(
            df
        )
    )

    if feasible.empty:

        return None

    return (

        feasible

        .sort_values(
            "system_total_loss",
            ascending=True,
        )

        .iloc[0]
    )


def find_best_converter_efficiency(
    df,
):

    if df.empty:

        return None

    thermal = (

        df[
            df[
                "thermal_feasible"
            ]
        ]

        .copy()
    )

    if thermal.empty:

        return None

    return (

        thermal

        .sort_values(
            "converter_efficiency",
            ascending=False,
        )

        .iloc[0]
    )


def find_lowest_cost_feasible(
    df,
):

    feasible = (
        get_fully_feasible_designs(
            df
        )
    )

    if feasible.empty:

        return None

    return (

        feasible

        .sort_values(
            "total_component_cost",
            ascending=True,
        )

        .iloc[0]
    )


def find_highest_power_density_feasible(
    df,
):

    feasible = (
        get_fully_feasible_designs(
            df
        )
    )

    if feasible.empty:

        return None

    return (

        feasible

        .sort_values(
            "power_density_kw_per_l",
            ascending=False,
        )

        .iloc[0]
    )


def find_minimum_converter_loss(
    df,
):

    feasible = (
        get_fully_feasible_designs(
            df
        )
    )

    if feasible.empty:

        return None

    return (

        feasible

        .sort_values(
            "converter_loss",
            ascending=True,
        )

        .iloc[0]
    )


def find_minimum_system_loss(
    df,
):

    feasible = (
        get_fully_feasible_designs(
            df
        )
    )

    if feasible.empty:

        return None

    return (

        feasible

        .sort_values(
            "system_total_loss",
            ascending=True,
        )

        .iloc[0]
    )