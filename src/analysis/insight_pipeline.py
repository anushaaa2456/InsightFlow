from src.kpi.snapshot import KPISnapshot
from src.detection.materiality import MaterialityEngine
from src.drivers.contributions import RevenueContributionEngine
from src.drivers.revenue_tree import RevenueDriverTree
from src.drivers.drivers_registry import DriverRegistry


class InsightPipeline:
    """
    Orchestrates InsightFlow's analytical reasoning pipeline.

    Pipeline:

        KPI Snapshot
             ↓
        Materiality
             ↓
        Driver Decomposition
             ↓
        Contribution
             ↓
        Investigation Output

    This layer coordinates existing analytical components.
    It does not duplicate their calculations.
    """

    def __init__(
        self,
        snapshot=None,
        materiality=None,
        contribution=None,
        driver_tree=None,
        driver_registry=None,
    ):

        self.snapshot = (
            snapshot
            or KPISnapshot()
        )

        self.materiality = (
            materiality
            or MaterialityEngine()
        )

        self.contribution = (
            contribution
            or RevenueContributionEngine()
        )

        self.driver_tree = (
            driver_tree
            or RevenueDriverTree()
        )

        self.driver_registry = (
            driver_registry
            or DriverRegistry()
        )

    # ==========================================================
    # SNAPSHOT
    # ==========================================================

    def _get_snapshot(
        self,
        kpi_name,
        entity_dimension,
        entity_value,
        previous_period,
        current_period,
    ):
        """
        Calculate the KPI movement for the requested entity
        and periods.
        """

        return self.snapshot.compare_periods(
            kpi_name=kpi_name,
            entity_dimension=entity_dimension,
            entity_value=entity_value,
            previous_period=previous_period,
            current_period=current_period,
        )

    # ==========================================================
    # MATERIALITY
    # ==========================================================

    def _evaluate_materiality(
        self,
        kpi_name,
        change_pct,
        expected_change_pct=None,
    ):
        """
        Determine whether the KPI movement warrants
        investigation.
        """

        return self.materiality.evaluate(
            kpi_name=kpi_name,
            change_pct=change_pct,
            expected_change_pct=expected_change_pct,
        )

    # ==========================================================
    # REVENUE DRIVER ANALYSIS
    # ==========================================================

    def _analyze_revenue_drivers(
        self,
        entity_value,
        previous_period,
        current_period,
    ):
        """
        Perform revenue driver decomposition.

        Revenue is currently the first KPI with a fully
        implemented driver contribution engine.
        """

        comparison = (
            self.driver_tree.compare_periods(
                region=entity_value,
                previous_period=previous_period,
                current_period=current_period,
            )
        )

        contribution = (
            self.contribution.calculate_contributions(
                comparison
            )
        )

        return {
            "comparison": comparison,
            "contribution": contribution,
        }

    # ==========================================================
    # MAIN PIPELINE
    # ==========================================================

    def analyze(
        self,
        kpi_name,
        entity_dimension,
        entity_value,
        previous_period,
        current_period,
        expected_change_pct=None,
    ):
        """
        Run the InsightFlow analytical pipeline.

        Parameters
        ----------
        kpi_name : str
            KPI to investigate.

        entity_dimension : str
            Dimension identifying the entity.

        entity_value : str
            Entity being investigated.

        previous_period : str
            Earlier period.

        current_period : str
            Current period.

        expected_change_pct : float, optional
            Expected percentage movement.

        Returns
        -------
        dict
            Structured analytical output.
        """

        # ------------------------------------------------------
        # 1. WHAT CHANGED?
        # ------------------------------------------------------

        snapshot = self._get_snapshot(
            kpi_name=kpi_name,
            entity_dimension=entity_dimension,
            entity_value=entity_value,
            previous_period=previous_period,
            current_period=current_period,
        )

        change_pct = snapshot["change_pct"]

        # ------------------------------------------------------
        # Handle undefined percentage change
        # ------------------------------------------------------

        if change_pct is None:

            return {
                "kpi": kpi_name,
                "entity_dimension": entity_dimension,
                "entity": entity_value,

                "previous_period": previous_period,
                "current_period": current_period,

                "snapshot": snapshot,

                "materiality": {
                    "is_material": False,
                    "decision": "INSUFFICIENT_BASELINE",
                },

                "investigation": None,
            }

        # ------------------------------------------------------
        # 2. IS THE CHANGE MATERIAL?
        # ------------------------------------------------------

        materiality = self._evaluate_materiality(
            kpi_name=kpi_name,
            change_pct=change_pct,
            expected_change_pct=expected_change_pct,
        )

        # ------------------------------------------------------
        # 3. STOP IF NOT MATERIAL
        # ------------------------------------------------------

        if not materiality["is_material"]:

            return {
                "kpi": kpi_name,
                "entity_dimension": entity_dimension,
                "entity": entity_value,

                "previous_period": previous_period,
                "current_period": current_period,

                "snapshot": snapshot,

                "materiality": materiality,

                "investigation": None,

                "decision": "NO_INVESTIGATION",
            }

        # ------------------------------------------------------
        # 4. INVESTIGATE
        # ------------------------------------------------------

        investigation = None

        if kpi_name == "revenue":

            if entity_dimension != "region":

                raise ValueError(
                    "The current revenue driver implementation "
                    "requires region-level analysis."
                )

            investigation = (
                self._analyze_revenue_drivers(
                    entity_value=entity_value,
                    previous_period=previous_period,
                    current_period=current_period,
                )
            )

        else:

            # --------------------------------------------------
            # Driver metadata is available for all registered
            # KPIs, but full contribution analysis is currently
            # implemented only for Revenue.
            # --------------------------------------------------

            investigation = {
                "drivers": (
                    self.driver_registry.get_driver_tree(
                        kpi_name
                    )
                ),
                "status": "DRIVER_ANALYSIS_NOT_IMPLEMENTED",
            }

        # ------------------------------------------------------
        # 5. FINAL STRUCTURED OUTPUT
        # ------------------------------------------------------

        result = {
            "kpi": kpi_name,
            "entity_dimension": entity_dimension,
            "entity": entity_value,

            "previous_period": previous_period,
            "current_period": current_period,

            "snapshot": snapshot,

            "materiality": materiality,

            "investigation": investigation,

            "decision": "INVESTIGATE",
        }

        # ------------------------------------------------------
        # Add primary driver when available
        # ------------------------------------------------------

        if (
            investigation
            and "contribution" in investigation
        ):

            contribution = (
                investigation["contribution"]
            )

            result["primary_driver"] = (
                contribution["primary_driver"]
            )

            result["drivers"] = (
                contribution["drivers"]
            )

        return result