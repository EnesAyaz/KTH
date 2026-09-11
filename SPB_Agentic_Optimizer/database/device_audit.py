from typing import Dict, List


# ==========================================================
# CORE PARAMETERS REQUIRED FOR DATABASE ENTRY
# ==========================================================

REQUIRED_FIELDS = [

    "part_number",

    "vds_rating",

    "rds_on_25c_mohm",

    "qg_nc",

    "rth_jc",

    "package_area_mm2",
]


# ==========================================================
# SWITCHING / CAPACITIVE DATA
#
# At least one useful capacitive representation
# should exist:
#
# Coss
# Qoss
# Eoss
#
# Qgd is useful but NOT universally mandatory for GaN.
# ==========================================================

IMPORTANT_OPTIONAL_FIELDS = [

    "id_continuous",

    "qgd_nc",

    "coss_pf",

    "qoss_nc",

    "eoss_uj",

    "eon_uj",

    "eoff_uj",

    "switching_test_voltage",

    "switching_test_current",

    "tj_max",
]


def audit_device_record(
    record: Dict,
):
    """
    Audit a candidate semiconductor record.

    The audit separates:

        database usability

    from:

        switching-model quality.

    A GaN device may be useful even when Qgd,
    Eon or Eoff are not provided by the manufacturer.
    """

    issues: List[str] = []

    warnings: List[str] = []

    # ======================================================
    # REQUIRED FIELDS
    # ======================================================

    for field in REQUIRED_FIELDS:

        value = record.get(
            field
        )

        if value is None:

            issues.append(
                f"Missing required field: {field}"
            )

    # ======================================================
    # OPTIONAL / HIGH-VALUE PARAMETERS
    # ======================================================

    for field in IMPORTANT_OPTIONAL_FIELDS:

        value = record.get(
            field
        )

        if value is None:

            warnings.append(
                f"Missing useful field: {field}"
            )

    # ======================================================
    # BASIC PHYSICAL VALIDATION
    # ======================================================

    vds = record.get(
        "vds_rating"
    )

    if vds is not None:

        if vds <= 0:

            issues.append(
                "VDS rating must be positive."
            )

        if vds > 2000:

            warnings.append(
                "VDS rating is unusually high for "
                "the present GaN database."
            )

    # ======================================================
    # CURRENT
    # ======================================================

    current = record.get(
        "id_continuous"
    )

    if current is not None:

        if current <= 0:

            issues.append(
                "Continuous drain current must be positive."
            )

    # ======================================================
    # RDS(ON)
    # ======================================================

    rds = record.get(
        "rds_on_25c_mohm"
    )

    if rds is not None:

        if rds <= 0:

            issues.append(
                "RDS(on) must be positive."
            )

        if rds > 1000:

            warnings.append(
                "RDS(on) is unusually large. "
                "Check extraction units."
            )

    # ======================================================
    # GATE CHARGE
    # ======================================================

    qg = record.get(
        "qg_nc"
    )

    if qg is not None:

        if qg <= 0:

            issues.append(
                "Qg must be positive."
            )

        if qg > 1000:

            warnings.append(
                "Qg is unusually large. "
                "Check extraction units."
            )

    # ======================================================
    # QGD
    # ======================================================

    qgd = record.get(
        "qgd_nc"
    )

    if (
        qgd is not None
        and qg is not None
    ):

        if qgd <= 0:

            issues.append(
                "Qgd must be positive when provided."
            )

        if qgd > qg:

            warnings.append(
                "Qgd exceeds total Qg. "
                "Verify the datasheet values and "
                "their test conditions."
            )

    # ======================================================
    # OUTPUT CAPACITANCE REPRESENTATIONS
    # ======================================================

    coss = record.get(
        "coss_pf"
    )

    qoss = record.get(
        "qoss_nc"
    )

    eoss = record.get(
        "eoss_uj"
    )

    if coss is not None:

        if coss <= 0:

            issues.append(
                "Coss must be positive."
            )

        if coss > 100000:

            warnings.append(
                "Coss appears unusually large. "
                "Check units."
            )

    if qoss is not None:

        if qoss <= 0:

            issues.append(
                "Qoss must be positive."
            )

    if eoss is not None:

        if eoss <= 0:

            issues.append(
                "Eoss must be positive."
            )

    # ------------------------------------------------------
    # At least one capacitive representation should exist.
    # ------------------------------------------------------

    if (
        coss is None
        and qoss is None
        and eoss is None
    ):

        issues.append(
            "No Coss, Qoss or Eoss information available."
        )

    # ======================================================
    # THERMAL
    # ======================================================

    rth = record.get(
        "rth_jc"
    )

    if rth is not None:

        if rth <= 0:

            issues.append(
                "RthJC must be positive."
            )

        if rth > 20:

            warnings.append(
                "RthJC appears unusually high."
            )

    tj_max = record.get(
        "tj_max"
    )

    if tj_max is not None:

        if tj_max < 100:

            warnings.append(
                "Maximum junction temperature is "
                "unusually low; verify extraction."
            )

        if tj_max > 250:

            warnings.append(
                "Maximum junction temperature is "
                "unusually high; verify extraction."
            )

    # ======================================================
    # PACKAGE
    # ======================================================

    package_area = record.get(
        "package_area_mm2"
    )

    if package_area is not None:

        if package_area <= 0:

            issues.append(
                "Package area must be positive."
            )

    # ======================================================
    # EOSS TEST CONDITIONS
    # ======================================================

    if (
        eoss is not None
        and record.get(
            "eoss_test_voltage"
        ) is None
    ):

        warnings.append(
            "Eoss exists but its test voltage "
            "has not been identified."
        )

    # ======================================================
    # COSS TEST CONDITIONS
    # ======================================================

    if (
        coss is not None
        and record.get(
            "coss_test_voltage"
        ) is None
    ):

        warnings.append(
            "Coss exists but its measurement voltage "
            "has not been identified."
        )

    # ======================================================
    # QOSS TEST CONDITIONS
    # ======================================================

    if (
        qoss is not None
        and record.get(
            "qoss_test_voltage"
        ) is None
    ):

        warnings.append(
            "Qoss exists but its test voltage "
            "has not been identified."
        )

    # ======================================================
    # SWITCHING ENERGY
    # ======================================================

    eon = record.get(
        "eon_uj"
    )

    eoff = record.get(
        "eoff_uj"
    )

    if (
        eon is not None
        or eoff is not None
    ):

        if record.get(
            "switching_test_voltage"
        ) is None:

            warnings.append(
                "Switching energy exists but "
                "test voltage is missing."
            )

        if record.get(
            "switching_test_current"
        ) is None:

            warnings.append(
                "Switching energy exists but "
                "test current is missing."
            )

    # ======================================================
    # SWITCHING MODEL CLASSIFICATION
    # ======================================================

    if (
        eon is not None
        and eoff is not None
    ):

        switching_model_level = (
            "datasheet_energy"
        )

    elif qgd is not None:

        switching_model_level = (
            "qgd_transition_model"
        )

    elif qg is not None:

        switching_model_level = (
            "qg_surrogate_required"
        )

        warnings.append(
            "Qgd and Eon/Eoff are unavailable. "
            "A lower-confidence switching transition "
            "model will be required."
        )

    else:

        switching_model_level = (
            "insufficient_switching_data"
        )

        issues.append(
            "Insufficient data for a switching-loss model."
        )

    # ======================================================
    # CONFIDENCE
    # ======================================================

    if len(
        issues
    ) > 0:

        confidence = "low"

    elif len(
        warnings
    ) <= 2:

        confidence = "high"

    else:

        confidence = "medium"

    return {

        "valid":
            len(
                issues
            ) == 0,

        "confidence":
            confidence,

        "switching_model_level":
            switching_model_level,

        "issues":
            issues,

        "warnings":
            warnings,

        "number_of_issues":
            len(
                issues
            ),

        "number_of_warnings":
            len(
                warnings
            ),
    }