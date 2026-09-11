from dataclasses import dataclass


@dataclass
class SystemConfig:

    # ==================================================
    # DC-LINK VOLTAGE
    # ==================================================

    vdc_nom: float = 1070.0
    vdc_max: float = 1250.0
    vdc_min: float = 700.0

    # ==================================================
    # OUTPUT POWER
    # ==================================================

    power_continuous: float = 300e3
    power_peak: float = 360e3

    # ==================================================
    # ELECTRICAL OPERATING POINT
    # ==================================================

    power_factor: float = 0.95

    # ==================================================
    # SWITCHING-FREQUENCY OPTIMIZATION
    # ==================================================

    fsw_min: float = 5e3
    fsw_max: float = 50e3
    fsw_step: float = 2.5e3

    # ==================================================
    # CONVERTER EFFICIENCY CONSTRAINT
    # ==================================================

    minimum_converter_efficiency: float = 0.995
    # 99.5 %

    # ==================================================
    # THERMAL
    # ==================================================

    coolant_temperature: float = 65.0

    max_junction_temperature: float = 150.0

    junction_temperature_margin: float = 25.0

    rth_case_to_coolant: float = 0.15

    max_parallel_devices: int = 12

    # ==================================================
    # SEMICONDUCTOR VOLTAGE DERATING
    # ==================================================

    device_voltage_derating: float = 0.80

    # ==================================================
    # SPB CELL COUNTS
    # ==================================================

    cell_counts: tuple = (
        3,
        4,
        5,
        6,
        8,
        10,
        12,
        15,
        16,
        18,
        20,
    )

    # ==================================================
    # DC-LINK CAPACITOR
    # ==================================================

    capacitor_voltage_ripple_fraction: float = 0.02

    capacitor_ripple_current_factor: float = 0.60

    capacitor_unit_capacitance: float = 100e-6

    capacitor_unit_voltage_rating: float = 500.0

    capacitor_unit_esr: float = 5e-3

    capacitor_unit_rms_current: float = 25.0

    capacitor_unit_price: float = 18.0

    capacitor_unit_volume_liter: float = 0.035

    capacitor_voltage_derating: float = 0.80

    minimum_cell_capacitance: float = 20e-6

    # ==================================================
    # GATE DRIVER / AUXILIARY
    # ==================================================

    gate_driver_quiescent_power_per_channel: float = 0.15

    isolator_power_per_channel: float = 0.05

    sensing_power_per_cell: float = 1.0

    controller_power_per_cell: float = 1.5

    isolated_supply_efficiency: float = 0.85

    isolated_supply_idle_power: float = 0.5

    isolated_supplies_per_cell: int = 1

    # ==================================================
    # AUXILIARY COST
    # ==================================================

    gate_driver_cost_per_channel: float = 3.0

    isolator_cost_per_channel: float = 1.5

    isolated_supply_cost_per_cell: float = 12.0

    sensing_cost_per_cell: float = 8.0

    controller_cost_per_cell: float = 10.0

    # ==================================================
    # AUXILIARY VOLUME
    # ==================================================

    gate_driver_volume_liter_per_channel: float = 0.0015

    isolator_volume_liter_per_channel: float = 0.0005

    isolated_supply_volume_liter_per_cell: float = 0.012

    sensing_volume_liter_per_cell: float = 0.005

    controller_volume_liter_per_cell: float = 0.008

    # ==================================================
    # PCB
    # ==================================================

    pcb_area_overhead_factor: float = 2.0

    pcb_thickness_mm: float = 1.6

    pcb_component_height_mm: float = 15.0

    pcb_cost_per_cm2: float = 0.10