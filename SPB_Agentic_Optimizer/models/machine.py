from models.provenance import (
    ModelEvidence,
)


def machine_harmonic_loss(
    fsw: float,
    reference_fsw: float = 10e3,
    reference_harmonic_loss: float = 2200.0,
    exponent: float = 1.0,
):
    """
    Preliminary machine harmonic-loss model.

    IMPORTANT:
    This is currently only a surrogate model.

    The assumed relationship is:

        P_harmonic =
            P_reference
            * (f_reference / fsw) ** exponent

    Higher switching frequency therefore reduces
    the estimated machine harmonic loss.

    Later this model should be replaced by:
        - FEM-derived loss maps,
        - measured machine-loss maps,
        - or validated literature-based models.

    Returns
    -------
    dict

    The dictionary contains:
        harmonic_loss
        evidence
    """

    # ==================================================
    # INPUT VALIDATION
    # ==================================================

    if fsw <= 0:

        raise ValueError(
            "Switching frequency must be positive."
        )

    if reference_fsw <= 0:

        raise ValueError(
            "reference_fsw must be positive."
        )

    if reference_harmonic_loss < 0:

        raise ValueError(
            "reference_harmonic_loss "
            "cannot be negative."
        )

    if exponent <= 0:

        raise ValueError(
            "exponent must be positive."
        )

    # ==================================================
    # HARMONIC LOSS MODEL
    # ==================================================

    harmonic_loss = (
        reference_harmonic_loss
        * (
            reference_fsw
            / fsw
        ) ** exponent
    )

    # ==================================================
    # MODEL PROVENANCE
    # ==================================================

    evidence = ModelEvidence(

        source_type="assumption",

        source_name=(
            "Temporary inverse-frequency "
            "machine harmonic-loss surrogate"
        ),

        confidence="low",

        notes=(
            "This model is used only to establish "
            "the optimization framework. "
            "Replace it with FEM, measurement, "
            "or literature-calibrated machine-loss data."
        ),

        reference_id=None,

        valid_min=5e3,

        valid_max=50e3,

        valid_unit="Hz",
    )

    # ==================================================
    # RETURN
    # ==================================================

    return {

        "harmonic_loss":
            harmonic_loss,

        "evidence":
            evidence,
    }