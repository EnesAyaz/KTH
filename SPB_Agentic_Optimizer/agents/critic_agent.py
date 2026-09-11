class CriticAgent:
    """
    Engineering critic for extracted semiconductor data.

    The Critic distinguishes:

        1. database completeness
        2. parameter ambiguity
        3. switching-model quality
        4. traceability quality
        5. optimizer suitability
    """

    def review(
        self,
        extraction_result,
    ):

        record = extraction_result[
            "record"
        ]

        audit = extraction_result[
            "audit"
        ]

        trace = extraction_result[
            "trace"
        ]

        findings = []

        recommendations = []

        # ==================================================
        # DATABASE COMPLETENESS
        # ==================================================

        if not audit[
            "valid"
        ]:

            findings.append(
                "Record does not satisfy minimum "
                "database requirements."
            )

        # ==================================================
        # AMBIGUOUS PARAMETERS
        # ==================================================

        important_parameters = [

            "vds",

            "id_continuous",

            "rds_on",

            "qg",

            "qgd",

            "coss",

            "qoss",

            "eoss",

            "rth_jc",

            "tj_max",
        ]

        ambiguous_parameters = []

        for parameter in (
            important_parameters
        ):

            candidates = (
                trace.get(
                    parameter
                )
            )

            if not isinstance(
                candidates,
                list,
            ):

                continue

            unique_values = set()

            for candidate in (
                candidates
            ):

                value = (
                    candidate.get(
                        "value"
                    )
                )

                if value is not None:

                    unique_values.add(
                        value
                    )

            if len(
                unique_values
            ) > 1:

                ambiguous_parameters.append(
                    {
                        "parameter":
                            parameter,

                        "values":
                            sorted(
                                unique_values
                            ),
                    }
                )

        # ==================================================
        # CRITICAL PARAMETERS
        # ==================================================

        critical_fields = [

            "vds_rating",

            "rds_on_25c_mohm",

            "qg_nc",

            "rth_jc",

            "package_area_mm2",
        ]

        missing_critical = []

        for field in (
            critical_fields
        ):

            if record.get(
                field
            ) is None:

                missing_critical.append(
                    field
                )

        # ==================================================
        # OUTPUT CAPACITANCE DATA
        # ==================================================

        has_coss = (
            record.get(
                "coss_pf"
            ) is not None
        )

        has_qoss = (
            record.get(
                "qoss_nc"
            ) is not None
        )

        has_eoss = (
            record.get(
                "eoss_uj"
            ) is not None
        )

        has_output_capacitance_data = (
            has_coss
            or has_qoss
            or has_eoss
        )

        if not has_output_capacitance_data:

            findings.append(
                "No usable Coss, Qoss or Eoss "
                "parameter is available."
            )

        # ==================================================
        # SWITCHING MODEL QUALITY
        # ==================================================

        has_eon_eoff = (
            record.get(
                "eon_uj"
            ) is not None
            and
            record.get(
                "eoff_uj"
            ) is not None
        )

        has_qgd = (
            record.get(
                "qgd_nc"
            ) is not None
        )

        has_qg = (
            record.get(
                "qg_nc"
            ) is not None
        )

        if has_eon_eoff:

            switching_model_status = (
                "HIGH: datasheet Eon/Eoff model available"
            )

            switching_confidence = (
                "high"
            )

        elif has_qgd:

            switching_model_status = (
                "MEDIUM: Qgd-based switching transition "
                "model available"
            )

            switching_confidence = (
                "medium"
            )

        elif has_qg:

            switching_model_status = (
                "LOW: Qgd and Eon/Eoff unavailable; "
                "Qg-based surrogate required"
            )

            switching_confidence = (
                "low"
            )

            recommendations.append(
                "Search datasheet curves, application notes "
                "or double-pulse-test data for switching "
                "transition information."
            )

        else:

            switching_model_status = (
                "UNAVAILABLE: insufficient switching data"
            )

            switching_confidence = (
                "unknown"
            )

        # ==================================================
        # COSS QUALITY
        # ==================================================

        if has_eoss:

            capacitive_model_status = (
                "Eoss data available"
            )

            capacitive_confidence = (
                "high"
            )

        elif has_qoss:

            capacitive_model_status = (
                "Qoss data available"
            )

            capacitive_confidence = (
                "medium"
            )

        elif has_coss:

            capacitive_model_status = (
                "Only scalar Coss available"
            )

            capacitive_confidence = (
                "low"
            )

            recommendations.append(
                "Prefer nonlinear Eoss(V) or Qoss(V) "
                "information over a single Coss value."
            )

        else:

            capacitive_model_status = (
                "No output-capacitance model available"
            )

            capacitive_confidence = (
                "unknown"
            )

        # ==================================================
        # TEST-CONDITION COMPLETENESS
        # ==================================================

        missing_test_conditions = []

        if (
            has_coss
            and record.get(
                "coss_test_voltage"
            ) is None
        ):

            missing_test_conditions.append(
                "coss_test_voltage"
            )

        if (
            has_qoss
            and record.get(
                "qoss_test_voltage"
            ) is None
        ):

            missing_test_conditions.append(
                "qoss_test_voltage"
            )

        if (
            has_eoss
            and record.get(
                "eoss_test_voltage"
            ) is None
        ):

            missing_test_conditions.append(
                "eoss_test_voltage"
            )

        if has_eon_eoff:

            if record.get(
                "switching_test_voltage"
            ) is None:

                missing_test_conditions.append(
                    "switching_test_voltage"
                )

            if record.get(
                "switching_test_current"
            ) is None:

                missing_test_conditions.append(
                    "switching_test_current"
                )

        # ==================================================
        # RECORD STATUS
        # ==================================================

        database_ready = (

            audit[
                "valid"
            ]

            and

            len(
                missing_critical
            ) == 0

            and

            has_output_capacitance_data
        )

        # --------------------------------------------------
        # Separate database readiness from model quality.
        # --------------------------------------------------

        if (
            database_ready
            and switching_confidence
            in [
                "high",
                "medium",
            ]
        ):

            approved_for_optimization = (
                True
            )

        elif database_ready:

            approved_for_optimization = (
                True
            )

            recommendations.append(
                "Device may be used in optimization, "
                "but switching-loss results must remain "
                "LOW confidence."
            )

        else:

            approved_for_optimization = (
                False
            )

        # ==================================================
        # OVERALL CONFIDENCE
        # ==================================================

        if not database_ready:

            confidence = "low"

        elif (
            len(
                ambiguous_parameters
            ) == 0
            and
            len(
                missing_test_conditions
            ) == 0
            and
            switching_confidence
            in [
                "high",
                "medium",
            ]
        ):

            confidence = "high"

        else:

            confidence = "medium"

        return {

            "database_ready":
                database_ready,

            "approved_for_optimization":
                approved_for_optimization,

            "confidence":
                confidence,

            "switching_confidence":
                switching_confidence,

            "capacitive_confidence":
                capacitive_confidence,

            "switching_model_status":
                switching_model_status,

            "capacitive_model_status":
                capacitive_model_status,

            "missing_critical":
                missing_critical,

            "missing_test_conditions":
                missing_test_conditions,

            "ambiguous_parameters":
                ambiguous_parameters,

            "findings":
                findings,

            "recommendations":
                recommendations,
        }


def print_critic_report(
    review,
):

    print("\n")
    print("=" * 100)
    print("CRITIC AGENT")
    print("=" * 100)

    print(
        f"""
Database ready:
    {review['database_ready']}

Approved for optimization:
    {review['approved_for_optimization']}

Overall confidence:
    {review['confidence']}

Switching-loss confidence:
    {review['switching_confidence']}

Capacitive-loss confidence:
    {review['capacitive_confidence']}

Switching model:
    {review['switching_model_status']}

Capacitive model:
    {review['capacitive_model_status']}
"""
    )

    if review[
        "missing_critical"
    ]:

        print(
            "Missing critical parameters:"
        )

        for parameter in (
            review[
                "missing_critical"
            ]
        ):

            print(
                f"    - {parameter}"
            )

    if review[
        "missing_test_conditions"
    ]:

        print(
            "\nMissing test conditions:"
        )

        for parameter in (
            review[
                "missing_test_conditions"
            ]
        ):

            print(
                f"    - {parameter}"
            )

    if review[
        "ambiguous_parameters"
    ]:

        print(
            "\nAmbiguous extracted parameters:"
        )

        for item in (
            review[
                "ambiguous_parameters"
            ]
        ):

            print(
                f"    - "
                f"{item['parameter']}: "
                f"{item['values']}"
            )

    if review[
        "findings"
    ]:

        print(
            "\nFindings:"
        )

        for finding in (
            review[
                "findings"
            ]
        ):

            print(
                f"    - {finding}"
            )

    if review[
        "recommendations"
    ]:

        print(
            "\nRecommendations:"
        )

        for recommendation in (
            review[
                "recommendations"
            ]
        ):

            print(
                f"    - {recommendation}"
            )