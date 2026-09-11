def estimate_pcb_size(
    semiconductor_area_mm2: float,
    n_cells: int,
    parallel_devices: int,
    config,
):
    """
    Preliminary PCB area / volume estimation.

    The semiconductor footprint is expanded by an
    overhead factor to account for:

        gate drivers
        isolation
        local decoupling
        sensing
        connectors
        creepage / clearance
        control electronics
        routing

    This is not a PCB routing tool.
    It is a parametric package-size estimator.
    """

    if semiconductor_area_mm2 <= 0:

        return {
            "pcb_area_mm2": 0.0,
            "pcb_area_cm2": 0.0,
            "pcb_volume_liter": 0.0,
            "pcb_cost": 0.0,
        }

    # ==================================================
    # PCB AREA
    # ==================================================

    pcb_area_mm2 = (
        semiconductor_area_mm2
        * config.pcb_area_overhead_factor
    )

    pcb_area_cm2 = (
        pcb_area_mm2
        / 100.0
    )

    # ==================================================
    # PCB ASSEMBLY HEIGHT
    # ==================================================

    total_height_mm = (
        config.pcb_thickness_mm
        + config.pcb_component_height_mm
    )

    # ==================================================
    # PCB VOLUME
    #
    # mm^3 -> liter
    #
    # 1 L = 1e6 mm^3
    # ==================================================

    pcb_volume_mm3 = (
        pcb_area_mm2
        * total_height_mm
    )

    pcb_volume_liter = (
        pcb_volume_mm3
        / 1e6
    )

    # ==================================================
    # PCB COST
    # ==================================================

    pcb_cost = (
        pcb_area_cm2
        * config.pcb_cost_per_cm2
    )

    # ==================================================
    # PER-CELL INFORMATION
    # ==================================================

    pcb_area_per_cell_mm2 = (
        pcb_area_mm2
        / n_cells
    )

    pcb_volume_per_cell_liter = (
        pcb_volume_liter
        / n_cells
    )

    return {

        "pcb_area_mm2":
            pcb_area_mm2,

        "pcb_area_cm2":
            pcb_area_cm2,

        "pcb_area_per_cell_mm2":
            pcb_area_per_cell_mm2,

        "pcb_volume_liter":
            pcb_volume_liter,

        "pcb_volume_per_cell_liter":
            pcb_volume_per_cell_liter,

        "pcb_cost":
            pcb_cost,
    }