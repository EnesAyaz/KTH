def calculate_constraint_metrics(
    result,
    config,
):
    """
    Calculate numerical margins for the
    principal hard constraints.

    Positive margin = constraint satisfied.
    """

    # ==================================================
    # THERMAL MARGIN
    # ==================================================

    thermal_margin_c = (
        result[
            "max_allowed_junction_temperature"
        ]
        - result[
            "junction_temperature"
        ]
    )

    # ==================================================
    # EFFICIENCY MARGIN
    # ==================================================

    minimum_efficiency_percent = (
        config.minimum_converter_efficiency
        * 100.0
    )

    converter_efficiency_margin_pp = (
        result[
            "converter_efficiency_percent"
        ]
        - minimum_efficiency_percent
    )

    # ==================================================
    # MAXIMUM ALLOWED CONVERTER LOSS
    # ==================================================

    maximum_converter_loss = (
        config.power_continuous
        * (
            1.0
            / config.minimum_converter_efficiency
            - 1.0
        )
    )

    # ==================================================
    # CONVERTER LOSS MARGIN
    # ==================================================

    converter_loss_margin_w = (
        maximum_converter_loss
        - result[
            "converter_loss"
        ]
    )

    return {

        "thermal_margin_c":
            thermal_margin_c,

        "converter_efficiency_margin_pp":
            converter_efficiency_margin_pp,

        "maximum_converter_loss_w":
            maximum_converter_loss,

        "converter_loss_margin_w":
            converter_loss_margin_w,
    }


def is_fully_feasible(
    result,
):
    """
    Hard constraint feasibility check.

    Current constraints:

        semiconductor voltage
        junction temperature
        converter efficiency
    """

    return (

        bool(
            result[
                "voltage_feasible"
            ]
        )

        and

        bool(
            result[
                "thermal_feasible"
            ]
        )

        and

        bool(
            result[
                "converter_efficiency_constraint_met"
            ]
        )
    )


def system_loss_objective(
    result,
):
    """
    Minimize converter + machine harmonic loss.
    """

    return result[
        "system_total_loss"
    ]


def converter_loss_objective(
    result,
):
    """
    Minimize converter loss.
    """

    return result[
        "converter_loss"
    ]


def cost_objective(
    result,
):
    """
    Minimize estimated component cost.
    """

    return result[
        "total_component_cost"
    ]


def volume_objective(
    result,
):
    """
    Minimize estimated converter volume.
    """

    return result[
        "total_estimated_volume_liter"
    ]


def power_density_objective(
    result,
):
    """
    Maximize power density.
    """

    return result[
        "power_density_kw_per_l"
    ]