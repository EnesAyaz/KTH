import math


def safe_fom(
    value_a,
    value_b,
):
    """
    Multiply two positive values safely.

    Returns None if either value is unavailable
    or non-positive.
    """

    if value_a is None:
        return None

    if value_b is None:
        return None

    if value_a <= 0:
        return None

    if value_b <= 0:
        return None

    return (
        value_a
        * value_b
    )


def calculate_device_foms(
    device,
):
    """
    Calculate semiconductor figures of merit.

    Fundamental units internally:

        Rds_on : ohm
        Qg     : coulomb
        Qgd    : coulomb
        Coss   : farad
        Eoss   : joule

    Human-readable FOM units are also returned.
    """

    # ==================================================
    # RDS * QG
    # ==================================================

    rds_qg_si = safe_fom(
        device.rds_on_25c,
        device.qg,
    )

    if rds_qg_si is not None:

        rds_qg_mohm_nc = (
            device.rds_on_25c
            * 1e3
            * device.qg
            * 1e9
        )

    else:

        rds_qg_mohm_nc = None

    # ==================================================
    # RDS * QGD
    # ==================================================

    rds_qgd_si = safe_fom(
        device.rds_on_25c,
        device.qgd,
    )

    if rds_qgd_si is not None:

        rds_qgd_mohm_nc = (
            device.rds_on_25c
            * 1e3
            * device.qgd
            * 1e9
        )

    else:

        rds_qgd_mohm_nc = None

    # ==================================================
    # RDS * COSS
    #
    # Preliminary only.
    #
    # Coss is voltage dependent, therefore this FOM
    # must not be treated as a rigorous cross-voltage
    # comparison unless Coss is measured at the same
    # voltage condition.
    # ==================================================

    rds_coss_si = safe_fom(
        device.rds_on_25c,
        device.coss,
    )

    if rds_coss_si is not None:

        rds_coss_mohm_pf = (
            device.rds_on_25c
            * 1e3
            * device.coss
            * 1e12
        )

    else:

        rds_coss_mohm_pf = None

    # ==================================================
    # RDS * EOSS
    #
    # Better capacitive FOM than raw Coss if Eoss
    # is available at a known voltage.
    # ==================================================

    if (
        device.eoss is not None
        and device.eoss > 0
    ):

        rds_eoss_si = (
            device.rds_on_25c
            * device.eoss
        )

        rds_eoss_mohm_uj = (
            device.rds_on_25c
            * 1e3
            * device.eoss
            * 1e6
        )

    else:

        rds_eoss_si = None
        rds_eoss_mohm_uj = None

    # ==================================================
    # SIMPLE CURRENT NORMALIZED RESISTANCE
    #
    # This is not a fundamental device FOM.
    # It is only a useful database descriptor.
    # ==================================================

    if device.id_continuous > 0:

        current_resistance_index = (
            device.rds_on_25c
            * device.id_continuous
        )

    else:

        current_resistance_index = None

    # ==================================================
    # RETURN
    # ==================================================

    return {

        "fom_rds_qg_si":
            rds_qg_si,

        "fom_rds_qg_mohm_nc":
            rds_qg_mohm_nc,

        "fom_rds_qgd_si":
            rds_qgd_si,

        "fom_rds_qgd_mohm_nc":
            rds_qgd_mohm_nc,

        "fom_rds_coss_si":
            rds_coss_si,

        "fom_rds_coss_mohm_pf":
            rds_coss_mohm_pf,

        "fom_rds_eoss_si":
            rds_eoss_si,

        "fom_rds_eoss_mohm_uj":
            rds_eoss_mohm_uj,

        "current_resistance_index":
            current_resistance_index,

        "fom_rds_qg_confidence":
            "medium",

        "fom_rds_qgd_confidence":
            "medium",

        "fom_rds_coss_confidence":
            "low",

        "fom_rds_eoss_confidence":
            (
                "high"
                if rds_eoss_si is not None
                else "unknown"
            ),

        "fom_notes":
            (
                "Rds*Qg and Rds*Qgd are useful device-level "
                "screening FOMs. Rds*Coss is only preliminary "
                "because Coss is nonlinear and voltage dependent. "
                "Prefer Rds*Eoss or Rds*Qoss when comparable "
                "voltage-dependent datasheet data are available."
            ),
    }


def percentage_improvement(
    reference_value,
    candidate_value,
):
    """
    Percentage improvement for a quantity where
    LOWER is better.

    Example:

        reference FOM = 100
        candidate FOM = 60

        improvement = 40 %
    """

    if reference_value is None:
        return None

    if candidate_value is None:
        return None

    if reference_value <= 0:
        return None

    return (
        (
            reference_value
            - candidate_value
        )
        /
        reference_value
        * 100.0
    )


def normalized_lower_is_better(
    value,
    minimum,
    maximum,
):
    """
    Normalize a lower-is-better quantity.

    Best = 1
    Worst = 0
    """

    if value is None:
        return None

    if maximum <= minimum:
        return 1.0

    return (
        1.0
        - (
            value
            - minimum
        )
        /
        (
            maximum
            - minimum
        )
    )