from models.provenance import (
    ModelEvidence,
)


def calculate_gate_driver_power(
    device,
    fsw: float,
    parallel_devices: int,
    gate_drive_voltage: float = 6.0,
):
    """
    Calculate dynamic gate-drive power.

    Formula:
        P_gate = Qg * Vg * fsw

    Returns the power for ONE switch position
    including all parallel devices.
    """

    if fsw <= 0:
        raise ValueError(
            "fsw must be positive."
        )

    if parallel_devices < 1:
        raise ValueError(
            "parallel_devices must be >= 1."
        )

    power_per_device = (
        device.qg
        * gate_drive_voltage
        * fsw
    )

    total_power = (
        power_per_device
        * parallel_devices
    )

    evidence = ModelEvidence(
        source_type="analytical",
        source_name="Qg * Vg * fsw",
        confidence="medium",
        notes=(
            "Qg is taken from the semiconductor "
            "device database. Replace database test "
            "values with real datasheet values later."
        ),
    )

    return {
        "power": total_power,
        "evidence": evidence,
    }


def evaluate_auxiliary_system(
    device,
    n_cells: int,
    fsw: float,
    parallel_devices: int,
    config,
):
    """
    Estimate auxiliary-system power, cost, and volume.

    Includes:
        - dynamic gate-drive power
        - driver quiescent power
        - digital isolator power
        - sensing power
        - controller power
        - isolated DC/DC conversion loss
        - isolated DC/DC idle power
    """

    if n_cells < 1:
        raise ValueError(
            "n_cells must be >= 1."
        )

    if parallel_devices < 1:
        raise ValueError(
            "parallel_devices must be >= 1."
        )

    # ==================================================
    # SWITCHING CHANNEL COUNT
    # ==================================================

    switch_positions_per_cell = 6

    total_switch_positions = (
        switch_positions_per_cell
        * n_cells
    )

    total_physical_devices = (
        total_switch_positions
        * parallel_devices
    )

    # ==================================================
    # DYNAMIC GATE POWER
    # ==================================================

    gate_result = calculate_gate_driver_power(
        device=device,
        fsw=fsw,
        parallel_devices=parallel_devices,
    )

    dynamic_gate_power_per_position = (
        gate_result["power"]
    )

    dynamic_gate_power_total = (
        dynamic_gate_power_per_position
        * total_switch_positions
    )

    # ==================================================
    # DRIVER QUIESCENT POWER
    # ==================================================

    driver_quiescent_power = (
        total_switch_positions
        * config.gate_driver_quiescent_power_per_channel
    )

    # ==================================================
    # ISOLATOR POWER
    # ==================================================

    isolator_power = (
        total_switch_positions
        * config.isolator_power_per_channel
    )

    # ==================================================
    # SENSING POWER
    # ==================================================

    sensing_power = (
        n_cells
        * config.sensing_power_per_cell
    )

    # ==================================================
    # CONTROLLER POWER
    # ==================================================

    controller_power = (
        n_cells
        * config.controller_power_per_cell
    )

    # ==================================================
    # TOTAL LOAD AFTER ISOLATED SUPPLY
    # ==================================================

    load_after_supply = (
        dynamic_gate_power_total
        + driver_quiescent_power
        + isolator_power
        + sensing_power
        + controller_power
    )

    # ==================================================
    # ISOLATED SUPPLY EFFICIENCY CHECK
    # ==================================================

    if (
        config.isolated_supply_efficiency <= 0
        or config.isolated_supply_efficiency > 1
    ):
        raise ValueError(
            "isolated_supply_efficiency "
            "must be between 0 and 1."
        )

    # ==================================================
    # SUPPLY INPUT POWER
    # ==================================================

    supply_input_power = (
        load_after_supply
        / config.isolated_supply_efficiency
    )

    supply_conversion_loss = (
        supply_input_power
        - load_after_supply
    )

    # ==================================================
    # SUPPLY IDLE POWER
    # ==================================================

    total_isolated_supplies = (
        n_cells
        * config.isolated_supplies_per_cell
    )

    supply_idle_power = (
        total_isolated_supplies
        * config.isolated_supply_idle_power
    )

    # ==================================================
    # TOTAL AUXILIARY POWER
    # ==================================================

    total_auxiliary_power = (
        supply_input_power
        + supply_idle_power
    )

    # ==================================================
    # COST MODEL
    # ==================================================

    gate_driver_cost = (
        total_switch_positions
        * config.gate_driver_cost_per_channel
    )

    isolator_cost = (
        total_switch_positions
        * config.isolator_cost_per_channel
    )

    supply_cost = (
        n_cells
        * config.isolated_supply_cost_per_cell
    )

    sensing_cost = (
        n_cells
        * config.sensing_cost_per_cell
    )

    controller_cost = (
        n_cells
        * config.controller_cost_per_cell
    )

    auxiliary_cost = (
        gate_driver_cost
        + isolator_cost
        + supply_cost
        + sensing_cost
        + controller_cost
    )

    # ==================================================
    # VOLUME MODEL
    # ==================================================

    driver_volume = (
        total_switch_positions
        * config.gate_driver_volume_liter_per_channel
    )

    isolator_volume = (
        total_switch_positions
        * config.isolator_volume_liter_per_channel
    )

    supply_volume = (
        n_cells
        * config.isolated_supply_volume_liter_per_cell
    )

    sensing_volume = (
        n_cells
        * config.sensing_volume_liter_per_cell
    )

    controller_volume = (
        n_cells
        * config.controller_volume_liter_per_cell
    )

    auxiliary_volume = (
        driver_volume
        + isolator_volume
        + supply_volume
        + sensing_volume
        + controller_volume
    )

    # ==================================================
    # MODEL EVIDENCE
    # ==================================================

    auxiliary_evidence = ModelEvidence(
        source_type="assumption",
        source_name=(
            "Generic auxiliary electronics model"
        ),
        confidence="low",
        notes=(
            "Driver quiescent power, isolator power, "
            "sensing power, controller power, isolated "
            "supply efficiency, cost, and volume are "
            "temporary assumptions. Replace them later "
            "with real datasheet and reference-design data."
        ),
    )

    # ==================================================
    # RETURN
    # ==================================================

    return {
        "switch_positions":
            total_switch_positions,

        "physical_devices":
            total_physical_devices,

        "dynamic_gate_power":
            dynamic_gate_power_total,

        "driver_quiescent_power":
            driver_quiescent_power,

        "isolator_power":
            isolator_power,

        "sensing_power":
            sensing_power,

        "controller_power":
            controller_power,

        "load_after_supply":
            load_after_supply,

        "supply_input_power":
            supply_input_power,

        "supply_conversion_loss":
            supply_conversion_loss,

        "supply_idle_power":
            supply_idle_power,

        "auxiliary_power":
            total_auxiliary_power,

        "gate_driver_cost":
            gate_driver_cost,

        "isolator_cost":
            isolator_cost,

        "supply_cost":
            supply_cost,

        "sensing_cost":
            sensing_cost,

        "controller_cost":
            controller_cost,

        "auxiliary_cost":
            auxiliary_cost,

        "driver_volume_liter":
            driver_volume,

        "isolator_volume_liter":
            isolator_volume,

        "supply_volume_liter":
            supply_volume,

        "sensing_volume_liter":
            sensing_volume,

        "controller_volume_liter":
            controller_volume,

        "auxiliary_volume_liter":
            auxiliary_volume,

        "gate_power_evidence":
            gate_result["evidence"],

        "auxiliary_evidence":
            auxiliary_evidence,
    }