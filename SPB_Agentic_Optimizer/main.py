import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config.system_config import (
    SystemConfig,
)

from database.device_loader import (
    load_gan_devices,
)

from optimization.optimizer import (
    run_full_design_space,
    find_system_sweet_point,
    find_best_converter_efficiency,
    find_lowest_cost_feasible,
    find_highest_power_density_feasible,
)

from optimization.pareto import (
    calculate_pareto_front,
    calculate_compromise_score,
    best_compromise_design,
)

from optimization.interpretation import (
    classify_architecture,
    short_architecture_summary,
    create_architecture_interpretation_table,
)


# ==========================================================
# OUTPUT DIRECTORY
# ==========================================================

os.makedirs(
    "results",
    exist_ok=True,
)


# ==========================================================
# CONFIGURATION
# ==========================================================

config = SystemConfig()


# ==========================================================
# CONVERTER LOSS LIMIT
# ==========================================================

maximum_converter_loss = (
    config.power_continuous
    * (
        1.0
        / config.minimum_converter_efficiency
        - 1.0
    )
)


# ==========================================================
# HEADER
# ==========================================================

print("\n")
print("=" * 120)
print("SPB AGENTIC OPTIMIZER")
print("=" * 120)


print(
    f"""
Rated output power:
    {config.power_continuous / 1000:.1f} kW

Nominal DC-link voltage:
    {config.vdc_nom:.1f} V

Maximum DC-link voltage:
    {config.vdc_max:.1f} V

Minimum converter efficiency:
    {config.minimum_converter_efficiency * 100:.3f} %

Maximum allowed converter loss:
    {maximum_converter_loss:.2f} W

Switching-frequency range:
    {config.fsw_min / 1000:.1f}
    -
    {config.fsw_max / 1000:.1f} kHz

Maximum parallel GaN devices:
    {config.max_parallel_devices}
"""
)


# ==========================================================
# LOAD DEVICES
# ==========================================================

devices = load_gan_devices(
    "database/gan_devices.xlsx"
)


print("=" * 120)
print("GaN DEVICES")
print("=" * 120)


for device in devices:

    print(
        f"{device.part_number:15s}"
        f" | "
        f"{device.vds_rating:6.0f} V"
        f" | "
        f"Rds(on) = "
        f"{device.rds_on_25c * 1e3:7.3f} mOhm"
    )


# ==========================================================
# RUN COMPLETE DESIGN SPACE
# ==========================================================

print("\n")
print("=" * 120)
print("RUNNING COMPLETE DESIGN SPACE")
print("=" * 120)


df, evaluated_count = (
    run_full_design_space(
        config=config,
        devices=devices,
    )
)


if df.empty:

    raise SystemExit(
        "No calculable designs found."
    )


print(
    f"Candidate combinations attempted: "
    f"{evaluated_count}"
)

print(
    f"Calculable combinations: "
    f"{len(df)}"
)


# ==========================================================
# SAVE ALL DESIGNS
# ==========================================================

df.to_excel(
    "results/"
    "all_designs_full_search.xlsx",
    index=False,
)


# ==========================================================
# FEASIBLE DESIGNS
# ==========================================================

feasible_df = (
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


print("\n")
print("=" * 120)
print("CONSTRAINT SUMMARY")
print("=" * 120)


print(
    f"Thermally feasible designs: "
    f"{int(df['thermal_feasible'].sum())}"
)

print(
    f"Designs satisfying converter-efficiency constraint: "
    f"{int(df['converter_efficiency_constraint_met'].sum())}"
)

print(
    f"Fully feasible designs: "
    f"{len(feasible_df)}"
)


feasible_df.to_excel(
    "results/"
    "feasible_designs_full_search.xlsx",
    index=False,
)


# ==========================================================
# HANDLE NO FEASIBLE DESIGN
# ==========================================================

if feasible_df.empty:

    best_converter = (
        find_best_converter_efficiency(
            df
        )
    )

    print("\n")
    print("=" * 120)
    print("NO FULLY FEASIBLE DESIGN FOUND")
    print("=" * 120)

    if best_converter is not None:

        print(
            f"""
Closest design:

Device:
    {best_converter['device']}

Voltage rating:
    {best_converter['voltage_rating']:.0f} V

Cells:
    {int(best_converter['cells'])}

Parallel devices:
    {int(best_converter['parallel_devices'])}

Switching frequency:
    {best_converter['fsw_khz']:.2f} kHz

Converter loss:
    {best_converter['converter_loss']:.2f} W

Converter efficiency:
    {best_converter['converter_efficiency_percent']:.4f} %

Required:
    {config.minimum_converter_efficiency * 100:.4f} %
"""
        )

        print("\nENGINEERING INTERPRETATION\n")

        print(
            short_architecture_summary(
                best_converter
            )
        )

    raise SystemExit


# ==========================================================
# REFERENCE OPTIMA
# ==========================================================

sweet_point = (
    find_system_sweet_point(
        df
    )
)


lowest_cost = (
    find_lowest_cost_feasible(
        df
    )
)


highest_density = (
    find_highest_power_density_feasible(
        df
    )
)


# ==========================================================
# EXACT PARETO FRONT
# ==========================================================

print("\n")
print("=" * 120)
print("CALCULATING EXACT PARETO FRONT")
print("=" * 120)


pareto_df = (
    calculate_pareto_front(
        df
    )
)


print(
    f"Feasible designs: "
    f"{len(feasible_df)}"
)

print(
    f"Pareto-optimal designs: "
    f"{len(pareto_df)}"
)


# ==========================================================
# ADD INTERPRETATION TO PARETO RESULTS
# ==========================================================

pareto_interpreted_df = (
    create_architecture_interpretation_table(
        pareto_df
    )
)


pareto_interpreted_df.to_excel(
    "results/"
    "pareto_with_interpretation.xlsx",
    index=False,
)


# ==========================================================
# SAVE PARETO
# ==========================================================

pareto_df.to_excel(
    "results/"
    "pareto_front.xlsx",
    index=False,
)


# ==========================================================
# PARETO COMPROMISE RANKING
# ==========================================================

ranked_pareto = (
    calculate_compromise_score(

        pareto_df=pareto_df,

        loss_weight=0.50,

        cost_weight=0.25,

        volume_weight=0.25,
    )
)


ranked_pareto = (
    create_architecture_interpretation_table(
        ranked_pareto
    )
)


ranked_pareto.to_excel(
    "results/"
    "pareto_ranked.xlsx",
    index=False,
)


compromise = (
    best_compromise_design(

        pareto_df=pareto_df,

        loss_weight=0.50,

        cost_weight=0.25,

        volume_weight=0.25,
    )
)


# ==========================================================
# MINIMUM SYSTEM LOSS DESIGN
# ==========================================================

print("\n")
print("=" * 120)
print("MINIMUM SYSTEM-LOSS DESIGN")
print("=" * 120)


print(
    f"""
Device:
    {sweet_point['device']}

Voltage class:
    {sweet_point['voltage_rating']:.0f} V

SPB cells:
    {int(sweet_point['cells'])}

Cell voltage:
    {sweet_point['cell_voltage']:.2f} V

Parallel GaN devices per switch:
    {int(sweet_point['parallel_devices'])}

Total GaN devices:
    {int(sweet_point['total_device_count'])}

Switching frequency:
    {sweet_point['fsw_khz']:.2f} kHz


CONVERTER
------------------------------------------------------------

Conduction loss:
    {sweet_point['conduction_loss']:.2f} W

Switching loss:
    {sweet_point['switching_loss']:.2f} W

Coss loss:
    {sweet_point['coss_loss']:.2f} W

Semiconductor loss:
    {sweet_point['semiconductor_loss']:.2f} W

Capacitor loss:
    {sweet_point['capacitor_loss']:.2f} W

Auxiliary power:
    {sweet_point['auxiliary_power']:.2f} W

Total converter loss:
    {sweet_point['converter_loss']:.2f} W

Converter efficiency:
    {sweet_point['converter_efficiency_percent']:.4f} %


MACHINE
------------------------------------------------------------

Machine harmonic loss:
    {sweet_point['machine_harmonic_loss']:.2f} W


SYSTEM
------------------------------------------------------------

Total optimized loss:
    {sweet_point['system_total_loss']:.2f} W

System efficiency:
    {sweet_point['system_efficiency_percent']:.4f} %


IMPLEMENTATION
------------------------------------------------------------

Estimated cost:
    {sweet_point['total_component_cost']:.2f}

Estimated volume:
    {sweet_point['total_estimated_volume_liter']:.4f} L

Power density:
    {sweet_point['power_density_kw_per_l']:.2f} kW/L
"""
)


print(
    "\nENGINEERING INTERPRETATION\n"
)


print(
    short_architecture_summary(
        sweet_point
    )
)


# ==========================================================
# LOWEST COST DESIGN
# ==========================================================

if lowest_cost is not None:

    print("\n")
    print("=" * 120)
    print("LOWEST-COST FEASIBLE DESIGN")
    print("=" * 120)

    print(
        short_architecture_summary(
            lowest_cost
        )
    )


# ==========================================================
# HIGHEST POWER DENSITY
# ==========================================================

if highest_density is not None:

    print("\n")
    print("=" * 120)
    print("HIGHEST-POWER-DENSITY FEASIBLE DESIGN")
    print("=" * 120)

    print(
        short_architecture_summary(
            highest_density
        )
    )


# ==========================================================
# PARETO COMPROMISE
# ==========================================================

if compromise is not None:

    print("\n")
    print("=" * 120)
    print("PARETO COMPROMISE DESIGN")
    print("=" * 120)


    print(
        """
Current compromise weights:

Loss:
    50 %

Cost:
    25 %

Volume:
    25 %
"""
    )


    print(
        short_architecture_summary(
            compromise
        )
    )


# ==========================================================
# SAVE IMPORTANT DESIGNS WITH INTERPRETATION
# ==========================================================

important_rows = []


if sweet_point is not None:

    sweet_dict = (
        sweet_point.to_dict()
    )

    sweet_dict[
        "design_role"
    ] = (
        "minimum_system_loss"
    )

    important_rows.append(
        sweet_dict
    )


if lowest_cost is not None:

    cost_dict = (
        lowest_cost.to_dict()
    )

    cost_dict[
        "design_role"
    ] = (
        "lowest_cost"
    )

    important_rows.append(
        cost_dict
    )


if highest_density is not None:

    density_dict = (
        highest_density.to_dict()
    )

    density_dict[
        "design_role"
    ] = (
        "highest_power_density"
    )

    important_rows.append(
        density_dict
    )


if compromise is not None:

    compromise_dict = (
        compromise.to_dict()
    )

    compromise_dict[
        "design_role"
    ] = (
        "pareto_compromise"
    )

    important_rows.append(
        compromise_dict
    )


important_df = pd.DataFrame(
    important_rows
)


important_df = (
    create_architecture_interpretation_table(
        important_df
    )
)


important_df.to_excel(
    "results/"
    "important_designs_with_interpretation.xlsx",
    index=False,
)


# ==========================================================
# PARETO ARCHITECTURE SUMMARY
# ==========================================================

pareto_architecture_summary = (
    pareto_df
    .groupby(
        [
            "device",
            "voltage_rating",
            "cells",
        ]
    )
    .agg(

        pareto_design_count=(
            "device",
            "size"
        ),

        minimum_system_loss=(
            "system_total_loss",
            "min"
        ),

        minimum_converter_loss=(
            "converter_loss",
            "min"
        ),

        maximum_converter_efficiency=(
            "converter_efficiency_percent",
            "max"
        ),

        minimum_cost=(
            "total_component_cost",
            "min"
        ),

        maximum_power_density=(
            "power_density_kw_per_l",
            "max"
        ),
    )
    .reset_index()
    .sort_values(
        "minimum_system_loss",
        ascending=True,
    )
)


pareto_architecture_summary.to_excel(
    "results/"
    "pareto_architecture_summary.xlsx",
    index=False,
)


# ==========================================================
# PRINT TOP PARETO ARCHITECTURES
# ==========================================================

print("\n")
print("=" * 120)
print("PARETO ARCHITECTURE INTERPRETATION")
print("=" * 120)


# Get the best system-loss Pareto design
# for every voltage/cell architecture.

representative_pareto = (
    pareto_df
    .sort_values(
        "system_total_loss"
    )
    .groupby(
        [
            "device",
            "cells",
        ],
        as_index=False,
    )
    .first()
)


representative_pareto = (
    representative_pareto
    .sort_values(
        "system_total_loss"
    )
)


for _, row in (
    representative_pareto
    .head(10)
    .iterrows()
):

    print()

    print(
        short_architecture_summary(
            row
        )
    )

    print(
        "-" * 80
    )


# ==========================================================
# NPARALLEL × FSW GRID
# ==========================================================

selected_device = (
    sweet_point[
        "device"
    ]
)


selected_cells = int(
    sweet_point[
        "cells"
    ]
)


architecture_df = (
    df[
        (
            df[
                "device"
            ]
            == selected_device
        )
        &
        (
            df[
                "cells"
            ]
            == selected_cells
        )
    ]
    .copy()
)


# ==========================================================
# LOSS GRID
# ==========================================================

loss_grid = (
    architecture_df
    .pivot_table(
        index="parallel_devices",
        columns="fsw_khz",
        values="converter_loss",
        aggfunc="first",
    )
    .sort_index()
)


loss_grid.to_excel(
    "results/"
    "parallel_fsw_converter_loss_grid.xlsx"
)


# ==========================================================
# EFFICIENCY GRID
# ==========================================================

efficiency_grid = (
    architecture_df
    .pivot_table(
        index="parallel_devices",
        columns="fsw_khz",
        values="converter_efficiency_percent",
        aggfunc="first",
    )
    .sort_index()
)


efficiency_grid.to_excel(
    "results/"
    "parallel_fsw_converter_efficiency_grid.xlsx"
)


# ==========================================================
# JUNCTION TEMPERATURE GRID
# ==========================================================

temperature_grid = (
    architecture_df
    .pivot_table(
        index="parallel_devices",
        columns="fsw_khz",
        values="junction_temperature",
        aggfunc="first",
    )
    .sort_index()
)


temperature_grid.to_excel(
    "results/"
    "parallel_fsw_junction_temperature_grid.xlsx"
)


# ==========================================================
# SYSTEM LOSS GRID
# ==========================================================

system_loss_grid = (
    architecture_df
    .pivot_table(
        index="parallel_devices",
        columns="fsw_khz",
        values="system_total_loss",
        aggfunc="first",
    )
    .sort_index()
)


system_loss_grid.to_excel(
    "results/"
    "parallel_fsw_system_loss_grid.xlsx"
)


# ==========================================================
# GENERIC GRID PLOTTER
# ==========================================================

def plot_grid(
    grid,
    title,
    colorbar_label,
    filename,
    number_format=".0f",
):

    fig, ax = plt.subplots(
        figsize=(14, 8)
    )

    values = (
        grid.values
    )

    image = ax.imshow(
        values,
        aspect="auto",
        origin="lower",
    )

    ax.set_xticks(
        np.arange(
            len(
                grid.columns
            )
        )
    )

    ax.set_xticklabels(
        [
            f"{value:.1f}"
            for value
            in grid.columns
        ],
        rotation=45,
        ha="right",
    )

    ax.set_yticks(
        np.arange(
            len(
                grid.index
            )
        )
    )

    ax.set_yticklabels(
        [
            str(value)
            for value
            in grid.index
        ]
    )

    ax.set_xlabel(
        "Switching Frequency [kHz]"
    )

    ax.set_ylabel(
        "Parallel GaN Devices per Switch Position"
    )

    ax.set_title(
        title
    )

    for row_index in range(
        values.shape[0]
    ):

        for column_index in range(
            values.shape[1]
        ):

            value = (
                values[
                    row_index,
                    column_index
                ]
            )

            if not np.isnan(
                value
            ):

                ax.text(
                    column_index,
                    row_index,
                    format(
                        value,
                        number_format
                    ),
                    ha="center",
                    va="center",
                    fontsize=7,
                )

    fig.colorbar(
        image,
        ax=ax,
        label=colorbar_label,
    )

    plt.tight_layout()

    plt.savefig(
        filename,
        dpi=300,
    )

    plt.show()


# ==========================================================
# CONVERTER LOSS HEATMAP
# ==========================================================

plot_grid(

    grid=loss_grid,

    title=(
        "Converter Loss Grid\n"
        f"{selected_device}, "
        f"{selected_cells} SPB Cells"
    ),

    colorbar_label=(
        "Converter Loss [W]"
    ),

    filename=(
        "results/"
        "parallel_fsw_converter_loss_grid.png"
    ),

    number_format=".0f",
)


# ==========================================================
# CONVERTER EFFICIENCY HEATMAP
# ==========================================================

plot_grid(

    grid=efficiency_grid,

    title=(
        "Converter Efficiency Grid\n"
        f"{selected_device}, "
        f"{selected_cells} SPB Cells"
    ),

    colorbar_label=(
        "Converter Efficiency [%]"
    ),

    filename=(
        "results/"
        "parallel_fsw_converter_efficiency_grid.png"
    ),

    number_format=".3f",
)


# ==========================================================
# JUNCTION TEMPERATURE HEATMAP
# ==========================================================

plot_grid(

    grid=temperature_grid,

    title=(
        "GaN Junction Temperature Grid\n"
        f"{selected_device}, "
        f"{selected_cells} SPB Cells"
    ),

    colorbar_label=(
        "Junction Temperature [C]"
    ),

    filename=(
        "results/"
        "parallel_fsw_junction_temperature_grid.png"
    ),

    number_format=".1f",
)


# ==========================================================
# SYSTEM LOSS HEATMAP
# ==========================================================

plot_grid(

    grid=system_loss_grid,

    title=(
        "Converter + Machine Harmonic Loss Grid\n"
        f"{selected_device}, "
        f"{selected_cells} SPB Cells"
    ),

    colorbar_label=(
        "System Loss [W]"
    ),

    filename=(
        "results/"
        "parallel_fsw_system_loss_grid.png"
    ),

    number_format=".0f",
)


# ==========================================================
# SWITCHING FREQUENCY LOSS BREAKDOWN
# ==========================================================

optimal_parallel = int(
    sweet_point[
        "parallel_devices"
    ]
)


tradeoff_df = (
    architecture_df[
        architecture_df[
            "parallel_devices"
        ]
        == optimal_parallel
    ]
    .sort_values(
        "fsw_khz"
    )
)


plt.figure(
    figsize=(11, 7)
)


plt.plot(
    tradeoff_df[
        "fsw_khz"
    ],
    tradeoff_df[
        "conduction_loss"
    ],
    marker="o",
    label="Conduction loss",
)


plt.plot(
    tradeoff_df[
        "fsw_khz"
    ],
    tradeoff_df[
        "switching_loss"
    ],
    marker="o",
    label="Switching overlap loss",
)


plt.plot(
    tradeoff_df[
        "fsw_khz"
    ],
    tradeoff_df[
        "coss_loss"
    ],
    marker="o",
    label="Coss loss",
)


plt.plot(
    tradeoff_df[
        "fsw_khz"
    ],
    tradeoff_df[
        "converter_loss"
    ],
    marker="o",
    label="Total converter loss",
)


plt.plot(
    tradeoff_df[
        "fsw_khz"
    ],
    tradeoff_df[
        "machine_harmonic_loss"
    ],
    marker="o",
    label="Machine harmonic loss",
)


plt.plot(
    tradeoff_df[
        "fsw_khz"
    ],
    tradeoff_df[
        "system_total_loss"
    ],
    marker="o",
    linewidth=2,
    label="Converter + machine harmonic loss",
)


plt.axhline(
    y=maximum_converter_loss,
    linestyle="--",
    label=(
        "99.5% converter-efficiency "
        "loss limit"
    ),
)


plt.xlabel(
    "Switching Frequency [kHz]"
)

plt.ylabel(
    "Loss [W]"
)

plt.title(
    (
        "Switching-Frequency Sweet Spot\n"
        f"{selected_device}, "
        f"{selected_cells} Cells, "
        f"Nparallel = {optimal_parallel}"
    )
)

plt.grid(
    True
)

plt.legend()

plt.tight_layout()


plt.savefig(
    "results/"
    "switching_frequency_loss_breakdown.png",
    dpi=300,
)


plt.show()


# ==========================================================
# PARETO: COST VS LOSS
# ==========================================================

plt.figure(
    figsize=(10, 7)
)


plt.scatter(
    feasible_df[
        "total_component_cost"
    ],
    feasible_df[
        "system_total_loss"
    ],
    alpha=0.25,
    label="Feasible designs",
)


plt.scatter(
    pareto_df[
        "total_component_cost"
    ],
    pareto_df[
        "system_total_loss"
    ],
    label="Pareto-optimal designs",
)


plt.xlabel(
    "Estimated Component Cost"
)

plt.ylabel(
    "Converter + Machine Harmonic Loss [W]"
)

plt.title(
    "SPB Pareto Front: Cost vs System Loss"
)

plt.grid(
    True
)

plt.legend()

plt.tight_layout()


plt.savefig(
    "results/"
    "pareto_cost_vs_loss.png",
    dpi=300,
)


plt.show()


# ==========================================================
# PARETO: POWER DENSITY VS LOSS
# ==========================================================

plt.figure(
    figsize=(10, 7)
)


plt.scatter(
    feasible_df[
        "power_density_kw_per_l"
    ],
    feasible_df[
        "system_total_loss"
    ],
    alpha=0.25,
    label="Feasible designs",
)


plt.scatter(
    pareto_df[
        "power_density_kw_per_l"
    ],
    pareto_df[
        "system_total_loss"
    ],
    label="Pareto-optimal designs",
)


plt.xlabel(
    "Estimated Power Density [kW/L]"
)

plt.ylabel(
    "Converter + Machine Harmonic Loss [W]"
)

plt.title(
    "SPB Pareto Front: Power Density vs System Loss"
)

plt.grid(
    True
)

plt.legend()

plt.tight_layout()


plt.savefig(
    "results/"
    "pareto_power_density_vs_loss.png",
    dpi=300,
)


plt.show()


# ==========================================================
# COMPLETE
# ==========================================================

print("\n")
print("=" * 120)
print("FILES CREATED")
print("=" * 120)


print(
    """
CORE RESULTS
------------------------------------------------------------
results/all_designs_full_search.xlsx
results/feasible_designs_full_search.xlsx

PARETO
------------------------------------------------------------
results/pareto_front.xlsx
results/pareto_ranked.xlsx
results/pareto_with_interpretation.xlsx
results/pareto_architecture_summary.xlsx

IMPORTANT DESIGNS
------------------------------------------------------------
results/important_designs_with_interpretation.xlsx

GRIDS
------------------------------------------------------------
results/parallel_fsw_converter_loss_grid.xlsx
results/parallel_fsw_converter_efficiency_grid.xlsx
results/parallel_fsw_junction_temperature_grid.xlsx
results/parallel_fsw_system_loss_grid.xlsx

FIGURES
------------------------------------------------------------
results/parallel_fsw_converter_loss_grid.png
results/parallel_fsw_converter_efficiency_grid.png
results/parallel_fsw_junction_temperature_grid.png
results/parallel_fsw_system_loss_grid.png
results/switching_frequency_loss_breakdown.png
results/pareto_cost_vs_loss.png
results/pareto_power_density_vs_loss.png
"""
)