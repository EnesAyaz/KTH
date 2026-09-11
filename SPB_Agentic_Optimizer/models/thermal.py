from models.semiconductor import (
    GaNDevice,
    semiconductor_losses,
)


def solve_junction_temperature(
    device: GaNDevice,
    phase_current_rms: float,
    phase_current_peak: float,
    cell_voltage: float,
    fsw: float,
    parallel_devices: int,
    coolant_temperature: float,
    rth_case_to_coolant: float,
    initial_temperature: float = 75.0,
    tolerance: float = 0.01,
    max_iterations: int = 100,
):

    tj = initial_temperature

    for iteration in range(
        max_iterations
    ):

        losses = semiconductor_losses(
            device=device,
            phase_current_rms=phase_current_rms,
            phase_current_peak=phase_current_peak,
            cell_voltage=cell_voltage,
            fsw=fsw,
            parallel_devices=parallel_devices,
            tj=tj,
        )

        # ==================================================
        # ONLY DEVICE HEAT CONTRIBUTES TO JUNCTION MODEL
        # ==================================================

        p_position_heat = (
            losses["device_heat_loss"]
        )

        p_device_heat = (
            p_position_heat
            / parallel_devices
        )

        total_rth = (
            device.rth_jc
            + rth_case_to_coolant
        )

        new_tj = (
            coolant_temperature
            + p_device_heat
            * total_rth
        )

        if abs(
            new_tj - tj
        ) < tolerance:

            return {

                "junction_temperature":
                    new_tj,

                "iterations":
                    iteration + 1,

                "losses":
                    losses,

                "thermal_converged":
                    True,
            }

        tj = new_tj

    return {

        "junction_temperature":
            tj,

        "iterations":
            max_iterations,

        "losses":
            losses,

        "thermal_converged":
            False,
    }


def find_parallel_device_count(
    device: GaNDevice,
    phase_current_rms: float,
    phase_current_peak: float,
    cell_voltage: float,
    fsw: float,
    coolant_temperature: float,
    rth_case_to_coolant: float,
    max_allowed_tj: float,
    max_parallel: int = 12,
):

    for parallel_devices in range(
        1,
        max_parallel + 1,
    ):

        result = solve_junction_temperature(
            device=device,
            phase_current_rms=phase_current_rms,
            phase_current_peak=phase_current_peak,
            cell_voltage=cell_voltage,
            fsw=fsw,
            parallel_devices=parallel_devices,
            coolant_temperature=coolant_temperature,
            rth_case_to_coolant=rth_case_to_coolant,
        )

        if not result[
            "thermal_converged"
        ]:
            continue

        if (
            result[
                "junction_temperature"
            ]
            <= max_allowed_tj
        ):

            result[
                "parallel_devices"
            ] = parallel_devices

            return result

    return None