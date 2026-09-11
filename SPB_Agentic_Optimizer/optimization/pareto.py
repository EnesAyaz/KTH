import numpy as np
import pandas as pd


def prepare_pareto_dataframe(
    df: pd.DataFrame,
):
    """
    Keep only fully feasible designs and prepare
    minimization objectives.

    Objectives
    ----------
    Minimize:
        system_total_loss
        total_component_cost
        total_estimated_volume_liter

    Equivalent to maximizing power density indirectly
    because lower volume at fixed rated power means
    higher power density.
    """

    if df.empty:
        return pd.DataFrame()

    feasible = (
        df[
            df["fully_feasible"]
        ]
        .copy()
        .reset_index(drop=True)
    )

    if feasible.empty:
        return feasible

    return feasible


def dominates(
    point_a,
    point_b,
):
    """
    Return True if point A dominates point B.

    For minimization objectives:

        A must be no worse in all objectives
        AND
        strictly better in at least one.
    """

    a = np.asarray(
        point_a,
        dtype=float,
    )

    b = np.asarray(
        point_b,
        dtype=float,
    )

    no_worse = np.all(
        a <= b
    )

    strictly_better = np.any(
        a < b
    )

    return (
        no_worse
        and strictly_better
    )


def calculate_pareto_front(
    df: pd.DataFrame,
    objective_columns=None,
):
    """
    Calculate exact Pareto front from the discrete
    feasible design population.
    """

    if objective_columns is None:

        objective_columns = [
            "system_total_loss",
            "total_component_cost",
            "total_estimated_volume_liter",
        ]

    feasible = (
        prepare_pareto_dataframe(
            df
        )
    )

    if feasible.empty:
        return feasible

    objective_matrix = (
        feasible[
            objective_columns
        ]
        .to_numpy(
            dtype=float
        )
    )

    n_points = len(
        feasible
    )

    pareto_mask = np.ones(
        n_points,
        dtype=bool,
    )

    for i in range(
        n_points
    ):

        if not pareto_mask[i]:
            continue

        for j in range(
            n_points
        ):

            if i == j:
                continue

            if dominates(
                objective_matrix[j],
                objective_matrix[i],
            ):

                pareto_mask[i] = False

                break

    pareto = (
        feasible[
            pareto_mask
        ]
        .copy()
        .reset_index(drop=True)
    )

    pareto[
        "pareto_optimal"
    ] = True

    return pareto


def normalize_series(
    series,
):
    """
    Min-max normalize a pandas Series.
    """

    minimum = (
        series.min()
    )

    maximum = (
        series.max()
    )

    if maximum == minimum:

        return (
            series
            * 0.0
        )

    return (
        (
            series
            - minimum
        )
        /
        (
            maximum
            - minimum
        )
    )


def calculate_compromise_score(
    pareto_df,
    loss_weight=0.50,
    cost_weight=0.25,
    volume_weight=0.25,
):
    """
    Calculate a simple weighted compromise score
    for Pareto-optimal solutions.

    Lower score is better.

    NOTE:
    This does NOT replace the Pareto front.
    It merely provides one convenient compromise
    candidate.
    """

    if pareto_df.empty:

        return pareto_df

    df = (
        pareto_df
        .copy()
    )

    df[
        "normalized_loss"
    ] = normalize_series(
        df[
            "system_total_loss"
        ]
    )

    df[
        "normalized_cost"
    ] = normalize_series(
        df[
            "total_component_cost"
        ]
    )

    df[
        "normalized_volume"
    ] = normalize_series(
        df[
            "total_estimated_volume_liter"
        ]
    )

    df[
        "compromise_score"
    ] = (

        loss_weight
        * df[
            "normalized_loss"
        ]

        +

        cost_weight
        * df[
            "normalized_cost"
        ]

        +

        volume_weight
        * df[
            "normalized_volume"
        ]
    )

    return (
        df
        .sort_values(
            "compromise_score",
            ascending=True,
        )
        .reset_index(drop=True)
    )


def best_compromise_design(
    pareto_df,
    loss_weight=0.50,
    cost_weight=0.25,
    volume_weight=0.25,
):
    """
    Return one weighted compromise design from the
    Pareto front.
    """

    ranked = (
        calculate_compromise_score(
            pareto_df=pareto_df,
            loss_weight=loss_weight,
            cost_weight=cost_weight,
            volume_weight=volume_weight,
        )
    )

    if ranked.empty:

        return None

    return ranked.iloc[0]