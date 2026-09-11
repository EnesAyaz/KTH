import numpy as np


def build_switching_frequency_values(
    config,
):
    """
    Generate switching-frequency candidates.
    """

    return np.arange(
        config.fsw_min,
        config.fsw_max
        + config.fsw_step,
        config.fsw_step,
    )


def build_parallel_device_values(
    config,
):
    """
    Generate parallel-device-count candidates.
    """

    return range(
        1,
        config.max_parallel_devices + 1,
    )


def generate_design_space(
    config,
    devices,
):
    """
    Generate the full discrete design space.

    Design variables:

        device
        N_cells
        fsw
        N_parallel
    """

    fsw_values = (
        build_switching_frequency_values(
            config
        )
    )

    parallel_values = (
        build_parallel_device_values(
            config
        )
    )

    for device in devices:

        for cells in config.cell_counts:

            for fsw in fsw_values:

                for parallel_devices in parallel_values:

                    yield {

                        "device":
                            device,

                        "cells":
                            cells,

                        "fsw":
                            float(fsw),

                        "parallel_devices":
                            int(
                                parallel_devices
                            ),
                    }