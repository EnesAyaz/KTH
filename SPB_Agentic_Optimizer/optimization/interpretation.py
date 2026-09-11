def classify_architecture(
    row,
):
    """
    Generate a human-readable engineering interpretation
    for one SPB design.

    This interpretation is currently rule-based.

    Later:
        Design Agent
        Critic Agent
        literature knowledge
        reference-design comparison

    can replace or enrich these rules.
    """

    cells = int(
        row["cells"]
    )

    voltage = float(
        row["voltage_rating"]
    )

    parallel = int(
        row["parallel_devices"]
    )

    device_count = int(
        row["total_device_count"]
    )

    auxiliary_power = float(
        row["auxiliary_power"]
    )

    cost = float(
        row["total_component_cost"]
    )

    volume = float(
        row["total_estimated_volume_liter"]
    )

    converter_loss = float(
        row["converter_loss"]
    )

    converter_efficiency = float(
        row["converter_efficiency_percent"]
    )

    system_loss = float(
        row["system_total_loss"]
    )

    power_density = float(
        row["power_density_kw_per_l"]
    )

    fsw = float(
        row["fsw_khz"]
    )

    # ==================================================
    # ARCHITECTURAL COMPLEXITY
    # ==================================================

    if cells <= 4:

        complexity = (
            "low architectural complexity"
        )

        cell_comment = (
            "few SPB cells result in fewer gate-driver, "
            "isolated-supply, sensing, control, and "
            "interconnection channels"
        )

    elif cells <= 10:

        complexity = (
            "moderate architectural complexity"
        )

        cell_comment = (
            "the architecture uses a moderate number of "
            "stacked cells and auxiliary channels"
        )

    else:

        complexity = (
            "high architectural complexity"
        )

        cell_comment = (
            "the large number of stacked cells increases "
            "gate-driver count, isolated supplies, sensing, "
            "control channels, PCB area, and interconnections"
        )

    # ==================================================
    # VOLTAGE CLASS CHARACTERISTIC
    # ==================================================

    if voltage >= 600:

        voltage_comment = (
            "The high-voltage GaN class enables a small "
            "number of SPB cells and therefore excellent "
            "architectural simplicity. The trade-off is "
            "typically poorer device-level conduction and "
            "switching FOM compared with lower-voltage GaN."
        )

    elif voltage >= 300:

        voltage_comment = (
            "The medium-voltage GaN class provides a "
            "compromise between semiconductor device "
            "performance and the number of stacked cells."
        )

    elif voltage >= 150:

        voltage_comment = (
            "The lower-voltage GaN class can provide "
            "improved semiconductor FOM, but requires more "
            "stacked cells and therefore increases system "
            "complexity."
        )

    else:

        voltage_comment = (
            "The very-low-voltage GaN class has strong "
            "device-level performance potential, but requires "
            "many stacked cells and substantially increases "
            "the number of drivers, auxiliary supplies, "
            "sensors, devices, and interconnections."
        )

    # ==================================================
    # PARALLELIZATION
    # ==================================================

    if parallel == 1:

        parallel_comment = (
            "No semiconductor paralleling is required, "
            "which simplifies current sharing and layout."
        )

    elif parallel <= 3:

        parallel_comment = (
            "Only modest semiconductor paralleling is needed, "
            "giving a reasonable balance between conduction "
            "loss and implementation complexity."
        )

    elif parallel <= 6:

        parallel_comment = (
            "A moderate number of parallel devices is required. "
            "This reduces conduction loss but increases Coss, "
            "gate-drive demand, cost, footprint, and current-"
            "sharing requirements."
        )

    else:

        parallel_comment = (
            "A large number of parallel devices is required. "
            "Although conduction resistance is reduced, the "
            "large device count increases capacitive switching "
            "loss, gate-drive power, cost, volume, and layout "
            "complexity."
        )

    # ==================================================
    # SWITCHING FREQUENCY
    # ==================================================

    if fsw <= 10:

        fsw_comment = (
            "The switching frequency is relatively low, "
            "favoring low converter switching loss but "
            "potentially increasing machine harmonic loss."
        )

    elif fsw <= 25:

        fsw_comment = (
            "The switching frequency is in a moderate range "
            "and represents a potential compromise between "
            "converter switching loss and machine harmonic loss."
        )

    else:

        fsw_comment = (
            "The switching frequency is relatively high. "
            "This can reduce machine harmonic content but "
            "increases semiconductor switching, Coss, and "
            "gate-drive losses."
        )

    # ==================================================
    # COMPLETE INTERPRETATION
    # ==================================================

    interpretation = (
        f"{voltage:.0f} V GaN with {cells} SPB cells has "
        f"{complexity}. "
        f"{cell_comment}. "
        f"{voltage_comment} "
        f"{parallel_comment} "
        f"{fsw_comment} "
        f"The present model predicts {converter_loss:.1f} W "
        f"converter loss, {converter_efficiency:.4f}% converter "
        f"efficiency, and {system_loss:.1f} W combined converter "
        f"plus machine harmonic loss. "
        f"The design uses {device_count} GaN devices, consumes "
        f"{auxiliary_power:.1f} W in the auxiliary system, has "
        f"an estimated cost of {cost:.1f}, estimated volume of "
        f"{volume:.3f} L, and estimated power density of "
        f"{power_density:.1f} kW/L."
    )

    return interpretation


def short_architecture_summary(
    row,
):
    """
    Generate concise engineering summary for terminal output.
    """

    cells = int(
        row["cells"]
    )

    voltage = float(
        row["voltage_rating"]
    )

    parallel = int(
        row["parallel_devices"]
    )

    devices = int(
        row["total_device_count"]
    )

    fsw = float(
        row["fsw_khz"]
    )

    converter_loss = float(
        row["converter_loss"]
    )

    efficiency = float(
        row["converter_efficiency_percent"]
    )

    machine_loss = float(
        row["machine_harmonic_loss"]
    )

    auxiliary_power = float(
        row["auxiliary_power"]
    )

    cost = float(
        row["total_component_cost"]
    )

    power_density = float(
        row["power_density_kw_per_l"]
    )

    # ==================================================
    # ARCHITECTURE LABEL
    # ==================================================

    if cells <= 4:

        architecture_label = (
            "excellent architectural simplicity"
        )

        auxiliary_label = (
            "low auxiliary-channel burden"
        )

    elif cells <= 10:

        architecture_label = (
            "moderate implementation complexity"
        )

        auxiliary_label = (
            "balanced auxiliary-system burden"
        )

    else:

        architecture_label = (
            "high implementation complexity"
        )

        auxiliary_label = (
            "many gate drivers, isolated supplies, "
            "sensors, and PCB sections"
        )

    # ==================================================
    # DEVICE-CLASS LABEL
    # ==================================================

    if voltage >= 600:

        device_label = (
            "high-voltage device class favors low cell count "
            "but may sacrifice semiconductor FOM"
        )

    elif voltage >= 300:

        device_label = (
            "mid-voltage device class provides a balanced "
            "device/system trade-off"
        )

    elif voltage >= 150:

        device_label = (
            "lower-voltage GaN improves device-level "
            "performance at the expense of more cells"
        )

    else:

        device_label = (
            "very-low-voltage GaN offers strong device FOM "
            "potential but requires many cells"
        )

    return (
        f"{voltage:.0f} V / {cells} cells\n"
        f"    {architecture_label}\n"
        f"    {auxiliary_label}\n"
        f"    {device_label}\n"
        f"    parallel devices per switch: {parallel}\n"
        f"    switching frequency: {fsw:.1f} kHz\n"
        f"    total GaN devices: {devices}\n"
        f"    converter loss: {converter_loss:.1f} W\n"
        f"    converter efficiency: {efficiency:.4f} %\n"
        f"    machine harmonic loss: {machine_loss:.1f} W\n"
        f"    auxiliary power: {auxiliary_power:.1f} W\n"
        f"    estimated cost: {cost:.1f}\n"
        f"    estimated power density: {power_density:.1f} kW/L"
    )


def create_architecture_interpretation_table(
    dataframe,
):
    """
    Add long and short textual interpretation columns
    to a design DataFrame.
    """

    if dataframe.empty:

        return dataframe.copy()

    result = (
        dataframe.copy()
    )

    result[
        "engineering_interpretation"
    ] = result.apply(
        classify_architecture,
        axis=1,
    )

    result[
        "short_interpretation"
    ] = result.apply(
        short_architecture_summary,
        axis=1,
    )

    return result