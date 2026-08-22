from src.kpi.registry import KPIRegistry


class MaterialityEngine:
    """
    Determines whether a KPI movement is materially significant
    enough to warrant investigation.

    Materiality is based on the KPI's semantic configuration
    in the registry.

    Current rules:

    1. Absolute period-over-period change exceeds the configured
       minimum threshold.

    2. Deviation from an expected value exceeds the configured
       threshold.

    The engine does not explain WHY a KPI changed.
    It only determines WHETHER the movement deserves investigation.
    """

    def __init__(self, registry=None):

        self.registry = registry or KPIRegistry()

    # ==========================================================
    # CONFIGURATION
    # ==========================================================

    def get_rules(self, kpi_name):
        """
        Return the materiality rules configured for a KPI.
        """

        return self.registry.get_materiality_rules(
            kpi_name
        )

    # ==========================================================
    # PERIOD-OVER-PERIOD MATERIALITY
    # ==========================================================

    def check_change(
        self,
        kpi_name,
        change_pct
    ):
        """
        Determine whether a period-over-period change
        is materially significant.

        Parameters
        ----------
        kpi_name : str
            Registered KPI.

        change_pct : float
            Percentage change between the current and
            comparison period.

        Returns
        -------
        dict
            Structured materiality result.
        """

        rules = self.get_rules(
            kpi_name
        )

        threshold = rules[
            "minimum_absolute_change_pct"
        ]

        absolute_change = abs(
            change_pct
        )

        is_material = (
            absolute_change >= threshold
        )

        return {
            "kpi": kpi_name,
            "change_pct": change_pct,
            "absolute_change_pct": absolute_change,
            "threshold_pct": threshold,
            "is_material": is_material,
            "reason": (
                f"Absolute change of "
                f"{absolute_change:.2f}% "
                f"{'meets' if is_material else 'does not meet'} "
                f"the materiality threshold of "
                f"{threshold:.2f}%."
            )
        }

    # ==========================================================
    # EXPECTED-VALUE MATERIALITY
    # ==========================================================

    def check_expected_deviation(
        self,
        kpi_name,
        actual_change_pct,
        expected_change_pct
    ):
        """
        Determine whether actual KPI movement deviates
        materially from the expected movement.

        Example:

            Actual:   -8%
            Expected: -1%

            Deviation = -7 percentage points

        """

        rules = self.get_rules(
            kpi_name
        )

        threshold = rules[
            "minimum_deviation_from_expected_pct"
        ]

        deviation = (
            actual_change_pct
            - expected_change_pct
        )

        absolute_deviation = abs(
            deviation
        )

        is_material = (
            absolute_deviation >= threshold
        )

        return {
            "kpi": kpi_name,
            "actual_change_pct": actual_change_pct,
            "expected_change_pct": expected_change_pct,
            "deviation_pct_points": deviation,
            "threshold_pct_points": threshold,
            "is_material": is_material,
            "reason": (
                f"Deviation of "
                f"{absolute_deviation:.2f} percentage points "
                f"{'meets' if is_material else 'does not meet'} "
                f"the expected-deviation threshold of "
                f"{threshold:.2f} percentage points."
            )
        }

    # ==========================================================
    # COMBINED DECISION
    # ==========================================================

    def evaluate(
        self,
        kpi_name,
        change_pct,
        expected_change_pct=None
    ):
        """
        Perform the complete materiality evaluation.

        A KPI is considered material when:

        - Its absolute change exceeds the configured
          period-over-period threshold

        OR

        - Its deviation from expected exceeds the configured
          expected-deviation threshold.

        If expected_change_pct is not available, only the
        period-over-period rule is evaluated.
        """

        change_result = self.check_change(
            kpi_name=kpi_name,
            change_pct=change_pct
        )

        expected_result = None

        if expected_change_pct is not None:

            expected_result = (
                self.check_expected_deviation(
                    kpi_name=kpi_name,
                    actual_change_pct=change_pct,
                    expected_change_pct=expected_change_pct
                )
            )

        is_material = (
            change_result["is_material"]
        )

        if expected_result is not None:

            is_material = (
                is_material
                or expected_result["is_material"]
            )

        if is_material:

            decision = "INVESTIGATE"

        else:

            decision = "NO_INVESTIGATION"

        return {
            "kpi": kpi_name,
            "is_material": is_material,
            "decision": decision,
            "period_change": change_result,
            "expected_deviation": expected_result
        }