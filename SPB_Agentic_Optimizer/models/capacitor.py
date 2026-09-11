import math

from models.provenance import (
    ModelEvidence,
)


def estimate_required_capacitance(
    cell_voltage: float,
    phase_current_peak: float,
    fsw: float,
    allowed_voltage_ripple_fraction: float,
    minimum_capacitance: float = 20e-6,
):
    """
    Preliminary analytical DC-link capacitance model.

    Approximation:

        C ~= I / (fsw * DeltaV)

    This is currently an engineering estimate.

    Later this should be replaced by:

        switching-state model
        capacitor current waveform
        numerical charge integration
    """

    if cell_voltage <= 0:
        raise ValueError(
            "cell_voltage must be positive."
        )

    if fsw <= 0:
        raise ValueError(
            "fsw must be positive."
        )

    if allowed_voltage_ripple_fraction <= 0:
        raise ValueError(
            "allowed_voltage_ripple_fraction "
            "must be positive."
        )

    delta_v_allowed = (
        cell_voltage
        * allowed_voltage_ripple_fraction
    )

    calculated_capacitance = (
        phase_current_peak
        /
        (
            fsw
            * delta_v_allowed
        )
    )

    required_capacitance = max(
        calculated_capacitance,
        minimum_capacitance,
    )

    evidence = ModelEvidence(

        source_type="assumption",

        source_name=(
            "First-order charge-balance "
            "capacitor sizing model"
        ),

        confidence="low",

        notes=(
            "Replace with SPB switching-state "
            "capacitor-current calculation."
        ),
    )

    return {

        "required_capacitance":
            required_capacitance,

        "delta_v_allowed":
            delta_v_allowed,

        "evidence":
            evidence,
    }


def estimate_capacitor_ripple_current(
    phase_current_rms: float,
    ripple_current_factor: float,
):
    """
    Preliminary capacitor RMS ripple-current model.
    """

    if ripple_current_factor < 0:
        raise ValueError(
            "ripple_current_factor cannot be negative."
        )

    current = (
        phase_current_rms
        * ripple_current_factor
    )

    evidence = ModelEvidence(

        source_type="assumption",

        source_name=(
            "Fixed capacitor ripple-current factor"
        ),

        confidence="low",

        notes=(
            "Current factor must later be replaced "
            "by PWM-derived capacitor RMS current."
        ),
    )

    return {

        "rms_current":
            current,

        "evidence":
            evidence,
    }


def design_capacitor_bank(
    required_capacitance: float,
    required_rms_current: float,
    cell_voltage: float,
    unit_capacitance: float,
    unit_voltage_rating: float,
    unit_esr: float,
    unit_rms_current: float,
    unit_price: float,
    unit_volume_liter: float,
    voltage_derating: float = 0.80,
):
    """
    Determine parallel capacitor quantity
    for one SPB cell.

    The capacitor unit parameters are currently
    provided by SystemConfig.

    Later they will come from an actual
    capacitor database.
    """

    if unit_capacitance <= 0:

        raise ValueError(
            "unit_capacitance must be positive."
        )

    if unit_voltage_rating <= 0:

        raise ValueError(
            "unit_voltage_rating must be positive."
        )

    if unit_rms_current <= 0:

        raise ValueError(
            "unit_rms_current must be positive."
        )

    allowable_voltage = (
        unit_voltage_rating
        * voltage_derating
    )

    if cell_voltage > allowable_voltage:

        return {

            "feasible":
                False,

            "reason":
                "capacitor_voltage_rating",
        }

    n_capacitance = math.ceil(
        required_capacitance
        / unit_capacitance
    )

    n_current = math.ceil(
        required_rms_current
        / unit_rms_current
    )

    number_parallel = max(
        1,
        n_capacitance,
        n_current,
    )

    actual_capacitance = (
        number_parallel
        * unit_capacitance
    )

    equivalent_esr = (
        unit_esr
        / number_parallel
    )

    current_per_capacitor = (
        required_rms_current
        / number_parallel
    )

    esr_loss = (
        required_rms_current**2
        * equivalent_esr
    )

    cost = (
        number_parallel
        * unit_price
    )

    volume = (
        number_parallel
        * unit_volume_liter
    )

    component_evidence = ModelEvidence(

        source_type="assumption",

        source_name=(
            "Generic test capacitor"
        ),

        confidence="low",

        notes=(
            "Replace with actual film capacitor "
            "manufacturer datasheet."
        ),
    )

    return {

        "feasible":
            True,

        "number_parallel":
            number_parallel,

        "required_capacitance":
            required_capacitance,

        "actual_capacitance":
            actual_capacitance,

        "required_rms_current":
            required_rms_current,

        "current_per_capacitor":
            current_per_capacitor,

        "equivalent_esr":
            equivalent_esr,

        "esr_loss":
            esr_loss,

        "cost":
            cost,

        "volume_liter":
            volume,

        "component_evidence":
            component_evidence,
    }


def evaluate_dc_link_capacitor(
    cell_voltage: float,
    phase_current_rms: float,
    phase_current_peak: float,
    fsw: float,
    config,
):
    """
    Complete preliminary DC-link capacitor
    evaluation for one SPB cell.
    """

    capacitance_result = (
        estimate_required_capacitance(

            cell_voltage=cell_voltage,

            phase_current_peak=(
                phase_current_peak
            ),

            fsw=fsw,

            allowed_voltage_ripple_fraction=(
                config
                .capacitor_voltage_ripple_fraction
            ),

            minimum_capacitance=(
                config.minimum_cell_capacitance
            ),
        )
    )

    ripple_result = (
        estimate_capacitor_ripple_current(

            phase_current_rms=(
                phase_current_rms
            ),

            ripple_current_factor=(
                config
                .capacitor_ripple_current_factor
            ),
        )
    )

    bank = design_capacitor_bank(

        required_capacitance=(
            capacitance_result[
                "required_capacitance"
            ]
        ),

        required_rms_current=(
            ripple_result[
                "rms_current"
            ]
        ),

        cell_voltage=cell_voltage,

        unit_capacitance=(
            config
            .capacitor_unit_capacitance
        ),

        unit_voltage_rating=(
            config
            .capacitor_unit_voltage_rating
        ),

        unit_esr=(
            config
            .capacitor_unit_esr
        ),

        unit_rms_current=(
            config
            .capacitor_unit_rms_current
        ),

        unit_price=(
            config
            .capacitor_unit_price
        ),

        unit_volume_liter=(
            config
            .capacitor_unit_volume_liter
        ),

        voltage_derating=(
            config
            .capacitor_voltage_derating
        ),
    )

    if not bank[
        "feasible"
    ]:

        return bank

    bank[
        "capacitance_model_evidence"
    ] = (
        capacitance_result[
            "evidence"
        ]
    )

    bank[
        "ripple_model_evidence"
    ] = (
        ripple_result[
            "evidence"
        ]
    )

    return bank