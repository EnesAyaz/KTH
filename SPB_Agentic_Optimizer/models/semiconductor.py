from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from models.provenance import (
    lowest_confidence,
)


@dataclass
class GaNDevice:

    manufacturer: str

    part_number: str

    vds_rating: float

    id_continuous: float

    rds_on_25c: float

    rds_temp_factor_125c: float

    qg: float

    qgd: Optional[float]

    coss: Optional[float]

    eoss: Optional[float]

    eon: Optional[float]

    eoff: Optional[float]

    eon_test_voltage: Optional[float]

    eon_test_current: Optional[float]

    rth_jc: float

    price: float

    package_area_mm2: float

    # ======================================================
    # OPTIONAL CURVE DATA
    # ======================================================

    rds_temperature_curve: list = field(
        default_factory=list
    )

    eoss_curve: list = field(
        default_factory=list
    )

    qoss_curve: list = field(
        default_factory=list
    )

    switching_energy_curve: list = field(
        default_factory=list
    )


# ==========================================================
# GENERIC 1D INTERPOLATION
# ==========================================================

def interpolate_curve(
    x,
    points,
    x_key,
    y_key,
):
    """
    Linear interpolation within a curve.

    Outside the curve range, the closest endpoint
    is used rather than uncontrolled extrapolation.
    """

    if not points:

        return None

    sorted_points = sorted(
        points,
        key=lambda item:
            item[
                x_key
            ],
    )

    x_values = np.array(
        [
            point[
                x_key
            ]
            for point
            in sorted_points
        ],
        dtype=float,
    )

    y_values = np.array(
        [
            point[
                y_key
            ]
            for point
            in sorted_points
        ],
        dtype=float,
    )

    if len(
        x_values
    ) == 1:

        return float(
            y_values[0]
        )

    # ------------------------------------------------------
    # Clamp rather than extrapolate
    # ------------------------------------------------------

    x_clamped = np.clip(
        x,
        x_values.min(),
        x_values.max(),
    )

    return float(
        np.interp(
            x_clamped,
            x_values,
            y_values,
        )
    )


# ==========================================================
# RDS(ON) TEMPERATURE
# ==========================================================

def rds_on_temperature(
    device,
    tj,
):
    """
    Model hierarchy:

    1. Datasheet normalized Rds(T) curve
    2. Scalar 125C temperature factor
    """

    # ======================================================
    # LEVEL 1: CURVE
    # ======================================================

    if (
        device.rds_temperature_curve
    ):

        multiplier = interpolate_curve(
            x=tj,
            points=device.rds_temperature_curve,
            x_key="temperature_c",
            y_key="rds_multiplier",
        )

        rds = (
            device.rds_on_25c
            * multiplier
        )

        return {

            "rds_on":
                rds,

            "multiplier":
                multiplier,

            "method":
                "datasheet_rds_temperature_curve",

            "confidence":
                "high",
        }

    # ======================================================
    # LEVEL 2: SCALAR FACTOR
    # ======================================================

    if (
        device.rds_temp_factor_125c
        is not None
        and
        device.rds_temp_factor_125c
        > 0
    ):

        if tj <= 25.0:

            multiplier = 1.0

        elif tj >= 125.0:

            multiplier = (
                device.rds_temp_factor_125c
            )

        else:

            multiplier = (
                1.0
                +
                (
                    device.rds_temp_factor_125c
                    - 1.0
                )
                *
                (
                    tj - 25.0
                )
                /
                100.0
            )

        return {

            "rds_on":
                device.rds_on_25c
                * multiplier,

            "multiplier":
                multiplier,

            "method":
                "linear_25c_to_125c_factor",

            "confidence":
                "medium",
        }

    # ======================================================
    # LEVEL 3: NO TEMPERATURE DATA
    # ======================================================

    return {

        "rds_on":
            device.rds_on_25c,

        "multiplier":
            1.0,

        "method":
            "constant_rds_no_temperature_model",

        "confidence":
            "low",
    }


# ==========================================================
# EOSS MODEL
# ==========================================================

def estimate_eoss(
    device,
    voltage,
):
    """
    Output-capacitive-energy hierarchy:

    1. Datasheet Eoss(V) curve
    2. Scalar datasheet Eoss
    3. Qoss(V) approximation
    4. Constant Coss approximation
    """

    # ======================================================
    # LEVEL 1: EOSS CURVE
    # ======================================================

    if device.eoss_curve:

        energy = interpolate_curve(
            x=voltage,
            points=device.eoss_curve,
            x_key="voltage_v",
            y_key="eoss_j",
        )

        return {

            "energy":
                energy,

            "method":
                "datasheet_eoss_curve",

            "confidence":
                "high",
        }

    # ======================================================
    # LEVEL 2: SCALAR EOSS
    # ======================================================

    if (
        device.eoss is not None
        and
        device.eoss > 0
    ):

        voltage_ratio = (
            voltage
            / device.vds_rating
        )

        energy = (
            device.eoss
            * voltage_ratio**2
        )

        return {

            "energy":
                energy,

            "method":
                "scalar_eoss_voltage_squared_scaling",

            "confidence":
                "medium",
        }

    # ======================================================
    # LEVEL 3: QOSS CURVE
    #
    # Approximation:
    #
    # E ~= 0.5 * Qoss(V) * V
    #
    # Better than constant Coss, but still not equivalent
    # to direct Eoss integration.
    # ======================================================

    if device.qoss_curve:

        qoss = interpolate_curve(
            x=voltage,
            points=device.qoss_curve,
            x_key="voltage_v",
            y_key="qoss_c",
        )

        energy = (
            0.5
            * qoss
            * voltage
        )

        return {

            "energy":
                energy,

            "method":
                "qoss_curve_energy_approximation",

            "confidence":
                "medium",
        }

    # ======================================================
    # LEVEL 4: CONSTANT COSS
    # ======================================================

    if (
        device.coss is not None
        and
        device.coss > 0
    ):

        energy = (
            0.5
            * device.coss
            * voltage**2
        )

        return {

            "energy":
                energy,

            "method":
                "constant_coss",

            "confidence":
                "low",
        }

    # ======================================================
    # NO MODEL
    # ======================================================

    return {

        "energy":
            0.0,

        "method":
            "missing_output_capacitance",

        "confidence":
            "unknown",
    }


# ==========================================================
# SWITCHING ENERGY CURVE INTERPOLATION
# ==========================================================

def estimate_switching_from_curve(
    device,
    voltage,
    current,
):
    """
    Use the closest voltage group and interpolate
    Eon/Eoff as functions of current.

    This is deliberately conservative and avoids
    uncontrolled 2D extrapolation.
    """

    if not device.switching_energy_curve:

        return None

    points = (
        device.switching_energy_curve
    )

    available_voltages = sorted(
        set(
            point[
                "voltage_v"
            ]
            for point
            in points
        )
    )

    if not available_voltages:

        return None

    # ------------------------------------------------------
    # Choose closest measured voltage
    # ------------------------------------------------------

    selected_voltage = min(
        available_voltages,
        key=lambda value:
            abs(
                value
                - voltage
            ),
    )

    voltage_points = [
        point
        for point
        in points
        if point[
            "voltage_v"
        ] == selected_voltage
    ]

    if not voltage_points:

        return None

    eon = interpolate_curve(
        x=current,
        points=voltage_points,
        x_key="current_a",
        y_key="eon_j",
    )

    eoff = interpolate_curve(
        x=current,
        points=voltage_points,
        x_key="current_a",
        y_key="eoff_j",
    )

    # ------------------------------------------------------
    # Voltage correction
    #
    # First-order scaling only.
    # ------------------------------------------------------

    if selected_voltage > 0:

        voltage_scale = (
            voltage
            / selected_voltage
        )

    else:

        voltage_scale = 1.0

    eon *= voltage_scale
    eoff *= voltage_scale

    confidence = (
        "high"
        if abs(
            voltage
            - selected_voltage
        )
        /
        max(
            selected_voltage,
            1.0
        )
        <= 0.10
        else
        "medium"
    )

    return {

        "eon":
            eon,

        "eoff":
            eoff,

        "reference_voltage":
            selected_voltage,

        "method":
            "switching_energy_curve",

        "confidence":
            confidence,
    }


# ==========================================================
# SWITCHING ENERGY
# ==========================================================

def estimate_switching_energy(
    device,
    voltage,
    current,
    rg_external=1.0,
    rg_driver=1.0,
    gate_drive_voltage=6.0,
    gate_plateau_voltage=2.5,
    qg_transition_fraction=0.20,
):
    """
    Hierarchy:

    1. Switching-energy curve
    2. Scalar Eon / Eoff
    3. Qgd overlap
    4. Qg surrogate
    """

    # ======================================================
    # LEVEL 1: CURVE
    # ======================================================

    curve_result = (
        estimate_switching_from_curve(
            device=device,
            voltage=voltage,
            current=current,
        )
    )

    if curve_result is not None:

        return curve_result

    # ======================================================
    # LEVEL 2: SCALAR DATASHEET ENERGY
    # ======================================================

    if (
        device.eon is not None
        and
        device.eoff is not None
        and
        device.eon_test_voltage is not None
        and
        device.eon_test_current is not None
        and
        device.eon_test_voltage > 0
        and
        device.eon_test_current > 0
    ):

        voltage_scale = (
            voltage
            / device.eon_test_voltage
        )

        current_scale = (
            current
            / device.eon_test_current
        )

        return {

            "eon":
                device.eon
                * voltage_scale
                * current_scale,

            "eoff":
                device.eoff
                * voltage_scale
                * current_scale,

            "method":
                "scalar_datasheet_energy",

            "confidence":
                "high",
        }

    # ======================================================
    # GATE CURRENT
    # ======================================================

    total_gate_resistance = (
        rg_external
        + rg_driver
    )

    voltage_margin = (
        gate_drive_voltage
        - gate_plateau_voltage
    )

    if total_gate_resistance <= 0:

        raise ValueError(
            "Gate resistance must be positive."
        )

    if voltage_margin <= 0:

        raise ValueError(
            "Gate drive voltage must exceed plateau voltage."
        )

    gate_current = (
        voltage_margin
        / total_gate_resistance
    )

    # ======================================================
    # LEVEL 3: QGD
    # ======================================================

    if (
        device.qgd is not None
        and
        device.qgd > 0
    ):

        transition_charge = (
            device.qgd
        )

        transition_time = (
            transition_charge
            / gate_current
        )

        energy = (
            0.5
            * voltage
            * current
            * transition_time
        )

        return {

            "eon":
                energy,

            "eoff":
                energy,

            "method":
                "qgd_overlap_model",

            "confidence":
                "medium",
        }

    # ======================================================
    # LEVEL 4: QG SURROGATE
    # ======================================================

    if (
        device.qg is not None
        and
        device.qg > 0
    ):

        transition_charge = (
            device.qg
            * qg_transition_fraction
        )

        transition_time = (
            transition_charge
            / gate_current
        )

        energy = (
            0.5
            * voltage
            * current
            * transition_time
        )

        return {

            "eon":
                energy,

            "eoff":
                energy,

            "qg_transition_fraction":
                qg_transition_fraction,

            "method":
                "qg_fraction_overlap_surrogate",

            "confidence":
                "low",
        }

    return {

        "eon":
            0.0,

        "eoff":
            0.0,

        "method":
            "missing_switching_model",

        "confidence":
            "unknown",
    }


# ==========================================================
# GATE DRIVE
# ==========================================================

def gate_drive_loss(
    device,
    fsw,
    gate_drive_voltage=6.0,
):

    if (
        device.qg is None
        or
        device.qg <= 0
    ):

        return 0.0

    return (
        device.qg
        * gate_drive_voltage
        * fsw
    )


# ==========================================================
# COMPLETE LOSS MODEL
# ==========================================================

def semiconductor_losses(
    device,
    phase_current_rms,
    phase_current_peak,
    cell_voltage,
    fsw,
    parallel_devices,
    tj,
):

    if parallel_devices < 1:

        raise ValueError(
            "parallel_devices must be >= 1."
        )

    # ======================================================
    # HOT RDS
    # ======================================================

    rds_result = (
        rds_on_temperature(
            device=device,
            tj=tj,
        )
    )

    rds_hot = (
        rds_result[
            "rds_on"
        ]
    )

    equivalent_rds = (
        rds_hot
        / parallel_devices
    )

    # ======================================================
    # CONDUCTION
    # ======================================================

    conduction_loss = (
        phase_current_rms**2
        * equivalent_rds
    )

    # ======================================================
    # CURRENT PER DEVICE
    # ======================================================

    current_per_device_peak = (
        phase_current_peak
        / parallel_devices
    )

    # ======================================================
    # SWITCHING
    # ======================================================

    switching = (
        estimate_switching_energy(
            device=device,
            voltage=cell_voltage,
            current=current_per_device_peak,
        )
    )

    switching_loss = (
        (
            switching[
                "eon"
            ]
            +
            switching[
                "eoff"
            ]
        )
        * fsw
        * parallel_devices
    )

    # ======================================================
    # OUTPUT CAPACITIVE LOSS
    # ======================================================

    eoss_result = (
        estimate_eoss(
            device=device,
            voltage=cell_voltage,
        )
    )

    coss_loss = (
        eoss_result[
            "energy"
        ]
        * fsw
        * parallel_devices
    )

    # ======================================================
    # GATE DRIVE
    # ======================================================

    gate_drive_power = (
        gate_drive_loss(
            device=device,
            fsw=fsw,
        )
        * parallel_devices
    )

    # ======================================================
    # DEVICE HEAT
    # ======================================================

    device_heat_loss = (
        conduction_loss
        + switching_loss
        + coss_loss
    )

    total_electrical_loss = (
        device_heat_loss
        + gate_drive_power
    )

    # ======================================================
    # CONFIDENCE
    # ======================================================

    overall_confidence = (
        lowest_confidence(
            rds_result[
                "confidence"
            ],
            switching[
                "confidence"
            ],
            eoss_result[
                "confidence"
            ],
        )
    )

    return {

        "conduction_loss":
            conduction_loss,

        "switching_loss":
            switching_loss,

        "coss_loss":
            coss_loss,

        "gate_drive_loss":
            gate_drive_power,

        "device_heat_loss":
            device_heat_loss,

        "total_loss":
            total_electrical_loss,

        "rds_on_hot":
            rds_hot,

        "rds_temperature_multiplier":
            rds_result[
                "multiplier"
            ],

        "rds_temperature_model":
            rds_result[
                "method"
            ],

        "rds_temperature_confidence":
            rds_result[
                "confidence"
            ],

        "current_per_device_peak":
            current_per_device_peak,

        "switching_model":
            switching[
                "method"
            ],

        "switching_confidence":
            switching[
                "confidence"
            ],

        "eoss_model":
            eoss_result[
                "method"
            ],

        "eoss_confidence":
            eoss_result[
                "confidence"
            ],

        "overall_confidence":
            overall_confidence,
    }