from src.kpi.snapshot import KPISnapshot
from src.detection.materiality import MaterialityEngine
from src.drivers.contributions import RevenueContributionEngine
from src.drivers.revenue_tree import RevenueDriverTree
from src.drivers.drivers_registry import DriverRegistry

from src.analysis.result import (
    AnalysisResult,
    DriverResult,
)


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
        Drill-down / Investigation
             ↓
        AnalysisResult

    This class coordinates the existing analytical components.
    It does not duplicate their calculations.

    Current fully implemented analytical path:

        Revenue → Region → Period Comparison
                → Materiality
                → Driver Decomposition
                → Contribution
                → Structured Result
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
        across the two requested periods.

        This answers:

            "What changed?"
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
        Determine whether the observed KPI movement
        warrants investigation.

        This answers:

            "Is the change significant enough to investigate?"
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
        Perform revenue driver decomposition and
        contribution analysis.

        Current revenue driver structure:

            Revenue
              ├── Customers
              ├── Orders per Customer
              └── AOV

        The contribution engine determines how much
        each driver contributed to the overall movement.
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
    # BUILD STANDARDIZED RESULT
    # ==========================================================

    def _build_result(
        self,
        snapshot,
        materiality,
        investigation=None,
    ):
        """
        Convert internal pipeline output into the stable
        AnalysisResult contract.

        This is the boundary between Person 1's analytical
        engine and downstream reasoning/evidence components.
        """

        drivers = []

        primary_driver = None

        # ------------------------------------------------------
        # Extract quantified drivers
        # ------------------------------------------------------

        if investigation:

            contribution = investigation.get(
                "contribution"
            )

            if contribution:

                raw_drivers = contribution.get(
                    "drivers",
                    []
                )

                drivers = [
                    DriverResult.from_dict(
                        driver
                    )
                    for driver in raw_drivers
                ]

                # --------------------------------------------------
                # Primary driver
                # --------------------------------------------------

                raw_primary = contribution.get(
                    "primary_driver"
                )

                if raw_primary:

                    primary_driver = (
                        DriverResult(
                            name=raw_primary["name"],
                            label=raw_primary["label"],
                            previous_value=raw_primary.get(
                                "previous_value"
                            ),
                            current_value=raw_primary.get(
                                "current_value"
                            ),
                            change_pct=raw_primary.get(
                                "change_pct"
                            ),
                            contribution_pp=raw_primary.get(
                                "contribution_pp"
                            ),
                            rank=raw_primary.get(
                                "rank"
                            ),
                        )
                    )

        # ------------------------------------------------------
        # Build standardized result
        # ------------------------------------------------------

        return AnalysisResult(

            kpi=snapshot["kpi"],

            entity_dimension=snapshot[
                "entity_dimension"
            ],

            entity=snapshot[
                "entity"
            ],

            previous_period=snapshot[
                "previous_period"
            ],

            current_period=snapshot[
                "current_period"
            ],

            previous_value=snapshot[
                "previous_value"
            ],

            current_value=snapshot[
                "current_value"
            ],

            absolute_change=snapshot[
                "absolute_change"
            ],

            change_pct=snapshot[
                "change_pct"
            ],

            direction=snapshot[
                "direction"
            ],

            is_material=materiality[
                "is_material"
            ],

            decision=materiality[
                "decision"
            ],

            drivers=drivers,

            primary_driver=primary_driver,
        )

    # ==========================================================
    # MAIN ANALYSIS PIPELINE
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
        Run the complete InsightFlow analytical pipeline.

        Parameters
        ----------
        kpi_name : str
            Registered KPI to investigate.

        entity_dimension : str
            Dimension identifying the entity.

            Example:
                "region"

        entity_value : str
            Entity being investigated.

            Example:
                "Region A"

        previous_period : str
            Earlier reporting period.

            Example:
                "2026-07"

        current_period : str
            Current reporting period.

            Example:
                "2026-08"

        expected_change_pct : float, optional
            Expected percentage movement.

        Returns
        -------
        AnalysisResult
            Standardized analytical result.
        """

        # ======================================================
        # STEP 1 — WHAT CHANGED?
        # ======================================================

        snapshot = self._get_snapshot(
            kpi_name=kpi_name,
            entity_dimension=entity_dimension,
            entity_value=entity_value,
            previous_period=previous_period,
            current_period=current_period,
        )

        change_pct = snapshot[
            "change_pct"
        ]

        # ======================================================
        # STEP 2 — HANDLE UNDEFINED BASELINE
        # ======================================================

        if change_pct is None:

            return AnalysisResult(

                kpi=kpi_name,

                entity_dimension=entity_dimension,

                entity=entity_value,

                previous_period=previous_period,

                current_period=current_period,

                previous_value=snapshot[
                    "previous_value"
                ],

                current_value=snapshot[
                    "current_value"
                ],

                absolute_change=snapshot[
                    "absolute_change"
                ],

                change_pct=None,

                direction=snapshot[
                    "direction"
                ],

                is_material=False,

                decision="INSUFFICIENT_BASELINE",
            )

        # ======================================================
        # STEP 3 — IS THE CHANGE MATERIAL?
        # ======================================================

        materiality = self._evaluate_materiality(
            kpi_name=kpi_name,
            change_pct=change_pct,
            expected_change_pct=expected_change_pct,
        )

        # ======================================================
        # STEP 4 — STOP IF NOT MATERIAL
        # ======================================================

        if not materiality[
            "is_material"
        ]:

            return self._build_result(
                snapshot=snapshot,
                materiality=materiality,
                investigation=None,
            )

        # ======================================================
        # STEP 5 — INVESTIGATE MATERIAL CHANGE
        # ======================================================

        investigation = None

        # ------------------------------------------------------
        # Revenue
        # ------------------------------------------------------

        if kpi_name == "revenue":

            if entity_dimension != "region":

                raise ValueError(
                    "The current revenue driver "
                    "implementation requires "
                    "region-level analysis."
                )

            investigation = (
                self._analyze_revenue_drivers(
                    entity_value=entity_value,
                    previous_period=previous_period,
                    current_period=current_period,
                )
            )

        # ------------------------------------------------------
        # Other registered KPIs
        # ------------------------------------------------------

        else:

            investigation = {
                "drivers": (
                    self.driver_registry.get_driver_tree(
                        kpi_name
                    )
                ),

                "status": (
                    "DRIVER_ANALYSIS_NOT_IMPLEMENTED"
                ),
            }

        # ======================================================
        # STEP 6 — BUILD FINAL ANALYSIS RESULT
        # ======================================================

        return self._build_result(
            snapshot=snapshot,
            materiality=materiality,
            investigation=investigation,
        )