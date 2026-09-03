from typing import Literal

from pydantic import BaseModel, Field


# =========================================================
# VALID COMPARISON DATABASE COLUMNS
# =========================================================

NumericColumn = Literal[
    "rated_power_kw",
    "peak_power_kw",
    "dc_link_voltage_v",
    "cell_voltage_v",
    "number_of_cells",
    "number_of_phases",
    "semiconductor_voltage_rating_v",
    "semiconductor_current_rating_a",
    "switching_frequency_khz",
    "efficiency_percent",
    "power_density_kw_per_l",
]


GroupColumn = Literal[
    "citation_key",
    "topology",
    "semiconductor_technology",
    "machine_type",
    "modulation_method",
    "cooling_method",
    "experimental_level",
]


PlotType = Literal[
    "scatter",
    "bar",
]


# =========================================================
# FIGURE SPECIFICATION
# =========================================================


class FigureSpec(BaseModel):
    """
    Specification for one quantitative review-paper figure.

    IMPORTANT:
    x_column and y_column can ONLY use numerical columns
    that actually exist in comparison.csv.
    """

    figure_id: str

    title: str

    purpose: str

    plot_type: PlotType

    # -----------------------------------------------------
    # DATA COLUMNS
    # -----------------------------------------------------

    x_column: NumericColumn | None = None

    y_column: NumericColumn

    group_column: GroupColumn | None = None

    # -----------------------------------------------------
    # AXIS LABELS
    # -----------------------------------------------------

    x_label: str | None = None

    y_label: str

    # -----------------------------------------------------
    # DATA REQUIREMENTS
    # -----------------------------------------------------

    required_columns: list[str] = Field(
        default_factory=list
    )

    minimum_rows: int = 2

    # -----------------------------------------------------
    # OUTPUT
    # -----------------------------------------------------

    latex_filename: str

    matlab_filename: str

    caption: str

    target_section: str

    scientific_message: str

    limitations: list[str] = Field(
        default_factory=list
    )


# =========================================================
# COMPLETE FIGURE PLAN
# =========================================================


class FigurePlan(BaseModel):
    """
    Complete collection of proposed scientific figures.
    """

    figures: list[FigureSpec]