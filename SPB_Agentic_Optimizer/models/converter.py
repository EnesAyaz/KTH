import numpy as np

from models.thermal import (
    find_parallel_device_count,
    solve_junction_temperature,
)

from models.machine import (
    machine_harmonic_loss,
)

from models.capacitor import (
    evaluate_dc_link_capacitor,
)

from models.auxiliary import (
    evaluate_auxiliary_system,
)

from models.pcb import (
    estimate_pcb_size,
)

from models.provenance import (
    lowest_confidence,
)


# ==========================================================
# PHASE CURRENT CALCULATION
# ==========================================================

def calculate_phase_current(
    power: float,
    vdc: float,
    power_factor: float,
):
    """
    Preliminary phase-current approximation.

    Assumption:

        V_phase_rms ~= Vdc / sqrt(6)

    This is temporary.

    Later this should be replaced using:
        modulation index,
        actual machine voltage,
        dq operating point,
        SPB winding arrangement.
    """

    if power <= 0:
        raise ValueError(
            "power must be positive."
        )

    if vdc <= 0:
        raise ValueError(
            "vdc must be positive."
        )

    if (
        power_factor <= 0
        or power_factor > 1
    ):
        raise ValueError(
            "power_factor must be between 0 and 1."
        )

    phase_voltage_rms = (
        vdc
        / np.sqrt(6)
    )

    phase_current_rms = (
        power
        /
        (
            3
            * phase_voltage_rms
            * power_factor
        )
    )

    phase_current_peak = (
        np.sqrt(2)
        * phase_current_rms
    )

    return (
        phase_current_rms,
        phase_current_peak,
    )


# ==========================================================
# DESIGN EVALUATION
# ==========================================================

def evaluate_design(
    config,
    device,
    n_cells: int,
    fsw: float,
    parallel_devices_override=None,
):
    """
    Evaluate one SPB converter design.

    Variables
    ---------
    device
    n_cells
    fsw

    Optional independent variable
    -----------------------------
    parallel_devices_override

    If parallel_devices_override is None:
        minimum thermally feasible parallel-device
        count is automatically selected.

    If parallel_devices_override is specified:
        that exact parallel count is evaluated.

    This allows N_parallel to become an independent
    optimization variable.
    """

    # ======================================================
    # BASIC VALIDATION
    # ======================================================

    if n_cells < 1:
        return None

    if fsw <= 0:
        return None

    # ======================================================
    # CELL VOLTAGE
    # ======================================================

    cell_voltage_max = (
        config.vdc_max
        / n_cells
    )

    # ======================================================
    # SEMICONDUCTOR VOLTAGE CONSTRAINT
    # ======================================================

    allowable_device_voltage = (
        config.device_voltage_derating
        * device.vds_rating
    )

    voltage_feasible = (
        cell_voltage_max
        <= allowable_device_voltage
    )

    if not voltage_feasible:
        return None

    # ======================================================
    # PHASE CURRENT
    # ======================================================

    (
        phase_current_rms,
        phase_current_peak,
    ) = calculate_phase_current(
        power=config.power_continuous,
        vdc=config.vdc_nom,
        power_factor=config.power_factor,
    )

    # ======================================================
    # MAXIMUM ALLOWED JUNCTION TEMPERATURE
    # ======================================================

    max_allowed_tj = (
        config.max_junction_temperature
        - config.junction_temperature_margin
    )

    # ======================================================
    # THERMAL MODEL
    # ======================================================

    if parallel_devices_override is None:

        # --------------------------------------------------
        # Automatically determine minimum thermally
        # feasible parallel-device count
        # --------------------------------------------------

        thermal = find_parallel_device_count(
            device=device,
            phase_current_rms=phase_current_rms,
            phase_current_peak=phase_current_peak,
            cell_voltage=cell_voltage_max,
            fsw=fsw,
            coolant_temperature=(
                config.coolant_temperature
            ),
            rth_case_to_coolant=(
                config.rth_case_to_coolant
            ),
            max_allowed_tj=max_allowed_tj,
            max_parallel=(
                config.max_parallel_devices
            ),
        )

        if thermal is None:
            return None

    else:

        # --------------------------------------------------
        # Explicitly evaluate requested N_parallel
        # --------------------------------------------------

        parallel_devices_override = int(
            parallel_devices_override
        )

        if (
            parallel_devices_override < 1
            or parallel_devices_override
            > config.max_parallel_devices
        ):
            return None

        thermal = solve_junction_temperature(
            device=device,
            phase_current_rms=phase_current_rms,
            phase_current_peak=phase_current_peak,
            cell_voltage=cell_voltage_max,
            fsw=fsw,
            parallel_devices=(
                parallel_devices_override
            ),
            coolant_temperature=(
                config.coolant_temperature
            ),
            rth_case_to_coolant=(
                config.rth_case_to_coolant
            ),
        )

        thermal[
            "parallel_devices"
        ] = parallel_devices_override

        if not thermal[
            "thermal_converged"
        ]:
            return None

    # ======================================================
    # THERMAL FEASIBILITY
    # ======================================================

    junction_temperature = (
        thermal[
            "junction_temperature"
        ]
    )

    thermal_feasible = (
        junction_temperature
        <= max_allowed_tj
    )

    # ======================================================
    # SEMICONDUCTOR LOSSES
    # ======================================================

    losses_position = (
        thermal[
            "losses"
        ]
    )

    switch_positions_per_cell = 6

    total_switch_positions = (
        switch_positions_per_cell
        * n_cells
    )

    parallel_devices = (
        thermal[
            "parallel_devices"
        ]
    )

    total_device_count = (
        total_switch_positions
        * parallel_devices
    )

    # ------------------------------------------------------
    # Conduction
    # ------------------------------------------------------

    conduction_loss = (
        losses_position[
            "conduction_loss"
        ]
        * total_switch_positions
    )

    # ------------------------------------------------------
    # Switching overlap
    # ------------------------------------------------------

    switching_loss = (
        losses_position[
            "switching_loss"
        ]
        * total_switch_positions
    )

    # ------------------------------------------------------
    # Coss
    # ------------------------------------------------------

    coss_loss = (
        losses_position[
            "coss_loss"
        ]
        * total_switch_positions
    )

    # ------------------------------------------------------
    # Semiconductor junction electrical loss
    #
    # Gate drive is NOT included here because it is
    # accounted for by auxiliary.py.
    # ------------------------------------------------------

    semiconductor_loss = (
        conduction_loss
        + switching_loss
        + coss_loss
    )

    # ======================================================
    # MACHINE HARMONIC LOSS
    # ======================================================

    machine_result = (
        machine_harmonic_loss(
            fsw=fsw,
            reference_fsw=10e3,
            reference_harmonic_loss=2200.0,
            exponent=1.0,
        )
    )

    machine_loss = (
        machine_result[
            "harmonic_loss"
        ]
    )

    # ======================================================
    # DC-LINK CAPACITOR
    # ======================================================

    capacitor = (
        evaluate_dc_link_capacitor(
            cell_voltage=(
                cell_voltage_max
            ),
            phase_current_rms=(
                phase_current_rms
            ),
            phase_current_peak=(
                phase_current_peak
            ),
            fsw=fsw,
            config=config,
        )
    )

    if not capacitor[
        "feasible"
    ]:
        return None

    capacitors_per_cell = (
        capacitor[
            "number_parallel"
        ]
    )

    total_capacitor_count = (
        capacitors_per_cell
        * n_cells
    )

    capacitor_loss = (
        capacitor[
            "esr_loss"
        ]
        * n_cells
    )

    capacitor_cost = (
        capacitor[
            "cost"
        ]
        * n_cells
    )

    capacitor_volume = (
        capacitor[
            "volume_liter"
        ]
        * n_cells
    )

    # ======================================================
    # AUXILIARY ELECTRONICS
    # ======================================================

    auxiliary = (
        evaluate_auxiliary_system(
            device=device,
            n_cells=n_cells,
            fsw=fsw,
            parallel_devices=(
                parallel_devices
            ),
            config=config,
        )
    )

    auxiliary_power = (
        auxiliary[
            "auxiliary_power"
        ]
    )

    # ======================================================
    # CONVERTER LOSS
    #
    # Machine loss is intentionally NOT included.
    # ======================================================

    converter_loss = (
        semiconductor_loss
        + capacitor_loss
        + auxiliary_power
    )

    # ======================================================
    # CONVERTER EFFICIENCY
    # ======================================================

    converter_efficiency = (
        config.power_continuous
        /
        (
            config.power_continuous
            + converter_loss
        )
    )

    converter_efficiency_percent = (
        converter_efficiency
        * 100.0
    )

    converter_efficiency_constraint_met = (
        converter_efficiency
        >= config.minimum_converter_efficiency
    )

    # ======================================================
    # SYSTEM LOSS
    #
    # This is the loss used for the switching-frequency
    # sweet-spot search.
    # ======================================================

    system_total_loss = (
        converter_loss
        + machine_loss
    )

    system_efficiency = (
        config.power_continuous
        /
        (
            config.power_continuous
            + system_total_loss
        )
    )

    system_efficiency_percent = (
        system_efficiency
        * 100.0
    )

    # ======================================================
    # COST
    # ======================================================

    semiconductor_cost = (
        total_device_count
        * device.price
    )

    semiconductor_area_mm2 = (
        total_device_count
        * device.package_area_mm2
    )

    # ======================================================
    # PCB SIZE
    # ======================================================

    pcb = (
        estimate_pcb_size(
            semiconductor_area_mm2=(
                semiconductor_area_mm2
            ),
            n_cells=n_cells,
            parallel_devices=(
                parallel_devices
            ),
            config=config,
        )
    )

    # ======================================================
    # TOTAL COMPONENT COST
    # ======================================================

    total_component_cost = (
        semiconductor_cost
        + capacitor_cost
        + auxiliary[
            "auxiliary_cost"
        ]
        + pcb[
            "pcb_cost"
        ]
    )

    # ======================================================
    # TOTAL VOLUME
    # ======================================================

    total_estimated_volume_liter = (
        capacitor_volume
        + auxiliary[
            "auxiliary_volume_liter"
        ]
        + pcb[
            "pcb_volume_liter"
        ]
    )

    # ======================================================
    # POWER DENSITY
    # ======================================================

    if (
        total_estimated_volume_liter
        > 0
    ):

        power_density_kw_per_l = (
            config.power_continuous
            / 1000.0
            / total_estimated_volume_liter
        )

    else:

        power_density_kw_per_l = 0.0

    # ======================================================
    # MODEL CONFIDENCE
    # ======================================================

    semiconductor_confidence = (
        losses_position[
            "overall_confidence"
        ]
    )

    machine_confidence = (
        machine_result[
            "evidence"
        ].confidence
    )

    capacitor_model_confidence = (
        capacitor[
            "capacitance_model_evidence"
        ].confidence
    )

    capacitor_component_confidence = (
        capacitor[
            "component_evidence"
        ].confidence
    )

    auxiliary_confidence = (
        auxiliary[
            "auxiliary_evidence"
        ].confidence
    )

    system_confidence = (
        lowest_confidence(
            semiconductor_confidence,
            machine_confidence,
            capacitor_model_confidence,
            capacitor_component_confidence,
            auxiliary_confidence,
        )
    )

    # ======================================================
    # COMPLETE RESULT
    # ======================================================

    return {

        # ==================================================
        # DEVICE
        # ==================================================

        "manufacturer":
            device.manufacturer,

        "device":
            device.part_number,

        "voltage_rating":
            device.vds_rating,

        # ==================================================
        # ARCHITECTURE
        # ==================================================

        "cells":
            n_cells,

        "cell_voltage":
            cell_voltage_max,

        "voltage_utilization":
            (
                cell_voltage_max
                / device.vds_rating
            ),

        "voltage_feasible":
            voltage_feasible,

        # ==================================================
        # SWITCHING FREQUENCY
        # ==================================================

        "fsw_khz":
            fsw / 1000.0,

        # ==================================================
        # CURRENT
        # ==================================================

        "phase_current_rms":
            phase_current_rms,

        "phase_current_peak":
            phase_current_peak,

        # ==================================================
        # PARALLEL DEVICES / THERMAL
        # ==================================================

        "parallel_devices":
            parallel_devices,

        "junction_temperature":
            junction_temperature,

        "max_allowed_junction_temperature":
            max_allowed_tj,

        "thermal_feasible":
            thermal_feasible,

        "total_device_count":
            total_device_count,

        # ==================================================
        # SEMICONDUCTOR LOSS
        # ==================================================

        "conduction_loss":
            conduction_loss,

        "switching_loss":
            switching_loss,

        "coss_loss":
            coss_loss,

        "semiconductor_loss":
            semiconductor_loss,

        # ==================================================
        # CAPACITOR
        # ==================================================

        "required_capacitance_per_cell_uF":
            (
                capacitor[
                    "required_capacitance"
                ]
                * 1e6
            ),

        "actual_capacitance_per_cell_uF":
            (
                capacitor[
                    "actual_capacitance"
                ]
                * 1e6
            ),

        "capacitors_per_cell":
            capacitors_per_cell,

        "total_capacitor_count":
            total_capacitor_count,

        "capacitor_rms_current_per_cell":
            capacitor[
                "required_rms_current"
            ],

        "capacitor_loss":
            capacitor_loss,

        "capacitor_cost":
            capacitor_cost,

        "capacitor_volume_liter":
            capacitor_volume,

        # ==================================================
        # AUXILIARY
        # ==================================================

        "dynamic_gate_power":
            auxiliary[
                "dynamic_gate_power"
            ],

        "driver_quiescent_power":
            auxiliary[
                "driver_quiescent_power"
            ],

        "isolator_power":
            auxiliary[
                "isolator_power"
            ],

        "sensing_power":
            auxiliary[
                "sensing_power"
            ],

        "controller_power":
            auxiliary[
                "controller_power"
            ],

        "auxiliary_power":
            auxiliary_power,

        "auxiliary_cost":
            auxiliary[
                "auxiliary_cost"
            ],

        "auxiliary_volume_liter":
            auxiliary[
                "auxiliary_volume_liter"
            ],

        # ==================================================
        # CONVERTER KPI
        # ==================================================

        "converter_loss":
            converter_loss,

        "converter_efficiency":
            converter_efficiency,

        "converter_efficiency_percent":
            converter_efficiency_percent,

        "converter_efficiency_constraint_met":
            converter_efficiency_constraint_met,

        # ==================================================
        # MACHINE
        # ==================================================

        "machine_harmonic_loss":
            machine_loss,

        # ==================================================
        # SYSTEM KPI
        # ==================================================

        "system_total_loss":
            system_total_loss,

        "system_efficiency":
            system_efficiency,

        "system_efficiency_percent":
            system_efficiency_percent,

        # Backward compatibility
        "total_loss":
            system_total_loss,

        "efficiency":
            system_efficiency,

        # ==================================================
        # COST
        # ==================================================

        "semiconductor_cost":
            semiconductor_cost,

        "total_component_cost":
            total_component_cost,

        # ==================================================
        # SIZE
        # ==================================================

        "semiconductor_area_mm2":
            semiconductor_area_mm2,

        "pcb_area_mm2":
            pcb[
                "pcb_area_mm2"
            ],

        "pcb_volume_liter":
            pcb[
                "pcb_volume_liter"
            ],

        "pcb_cost":
            pcb[
                "pcb_cost"
            ],

        "total_estimated_volume_liter":
            total_estimated_volume_liter,

        "power_density_kw_per_l":
            power_density_kw_per_l,

        # ==================================================
        # PROVENANCE / CONFIDENCE
        # ==================================================

        "semiconductor_confidence":
            semiconductor_confidence,

        "machine_model_source":
            machine_result[
                "evidence"
            ].source_name,

        "machine_confidence":
            machine_confidence,

        "capacitor_model_source":
            capacitor[
                "capacitance_model_evidence"
            ].source_name,

        "capacitor_model_confidence":
            capacitor_model_confidence,

        "capacitor_component_source":
            capacitor[
                "component_evidence"
            ].source_name,

        "capacitor_component_confidence":
            capacitor_component_confidence,

        "auxiliary_model_source":
            auxiliary[
                "auxiliary_evidence"
            ].source_name,

        "auxiliary_confidence":
            auxiliary_confidence,

        "system_confidence":
            system_confidence,

        # ==================================================
        # SEMICONDUCTOR MODEL TRACEABILITY
        # ==================================================

        "switching_model":
            losses_position[
                "switching_model"
            ],

        "switching_confidence":
            losses_position[
                "switching_confidence"
            ],

        "eoss_model":
            losses_position[
                "eoss_model"
            ],

        "eoss_confidence":
            losses_position[
                "eoss_confidence"
            ],
    }