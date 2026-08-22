from src.kpi.registry import KPIRegistry


class MaterialityEngine:
    """
    Determines whether a KPI movement is materially different
    from expected or normal performance.

    This engine does not explain WHY the KPI moved.
    It only determines whether the movement warrants investigation.
    """

    def __init__(self, registry=None):
        self.registry = registry or KPIRegistry()

    def evaluate(
        self,
        kpi_name,
        change_pct,
        expected_change_pct=None,
        peer_changes=None,
    ):
        """
        Evaluate whether a KPI movement is material.

        Parameters
        ----------
        kpi_name : str
            Registered KPI name.

        change_pct : float
            Observed percentage change.

        expected_change_pct : float, optional
            Expected percentage change for the same period.

        peer_changes : dict, optional
            Percentage changes for comparable entities.

            Example:
            {
                "Region B": 0.47,
                "Region C": 0.45,
                "Region D": -0.88
            }

        Returns
        -------
        dict
            Materiality assessment.
        """

        # --------------------------------------------------
        # Load materiality rules
        # --------------------------------------------------

        rules = self.registry.get_materiality_rules(
            kpi_name
        )

        minimum_absolute_change = rules[
            "minimum_absolute_change_pct"
        ]

        minimum_expected_deviation = rules[
            "minimum_deviation_from_expected_pct"
        ]

        # --------------------------------------------------
        # Signal 1 — Absolute movement
        # --------------------------------------------------

        absolute_change = abs(change_pct)

        exceeds_absolute_threshold = (
            absolute_change
            >= minimum_absolute_change
        )

        # --------------------------------------------------
        # Signal 2 — Deviation from expected
        # --------------------------------------------------

        expected_deviation = None
        exceeds_expected_threshold = False

        if expected_change_pct is not None:

            expected_deviation = (
                change_pct - expected_change_pct
            )

            exceeds_expected_threshold = (
                abs(expected_deviation)
                >= minimum_expected_deviation
            )

        # --------------------------------------------------
        # Signal 3 — Peer context
        # --------------------------------------------------

        peer_context = None
        peer_outlier = False

        if peer_changes:

            peer_values = list(
                peer_changes.values()
            )

            if peer_values:

                peer_mean = sum(peer_values) / len(
                    peer_values
                )

                peer_context = {
                    "peer_mean_change_pct": round(
                        peer_mean,
                        2
                    ),
                    "entity_change_pct": round(
                        change_pct,
                        2
                    ),
                    "difference_from_peer_mean_pct": round(
                        change_pct - peer_mean,
                        2
                    ),
                }

                # A simple first-pass peer signal:
                # flag if entity differs from peer mean
                # by at least the absolute-change threshold.
                peer_outlier = (
                    abs(change_pct - peer_mean)
                    >= minimum_absolute_change
                )

        # --------------------------------------------------
        # Overall materiality decision
        # --------------------------------------------------

        signals = {
            "absolute_change": exceeds_absolute_threshold,
            "expected_deviation": exceeds_expected_threshold,
            "peer_outlier": peer_outlier,
        }

        positive_signals = sum(
            signals.values()
        )

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        if positive_signals >= 2:

            materiality = "HIGH"

        elif positive_signals == 1:

            materiality = "MEDIUM"

        else:

            materiality = "LOW"

        # --------------------------------------------------
        # Investigation decision
        # --------------------------------------------------

        investigate = materiality in {
            "HIGH",
            "MEDIUM"
        }

        # --------------------------------------------------
        # Build result
        # --------------------------------------------------

        result = {

            "kpi": kpi_name,

            "observed_change_pct": round(
                change_pct,
                2
            ),

            "expected_change_pct": (
                round(
                    expected_change_pct,
                    2
                )
                if expected_change_pct is not None
                else None
            ),

            "deviation_from_expected_pct": (
                round(
                    expected_deviation,
                    2
                )
                if expected_deviation is not None
                else None
            ),

            "thresholds": {
                "minimum_absolute_change_pct":
                    minimum_absolute_change,

                "minimum_deviation_from_expected_pct":
                    minimum_expected_deviation,
            },

            "signals": signals,

            "peer_context": peer_context,

            "materiality": materiality,

            "investigate": investigate,
        }

        return result