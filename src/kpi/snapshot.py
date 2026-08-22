from src.kpi.calculator import KPICalculator


class KPISnapshot:
    """
    Creates a structured comparison between two reporting periods.

    This layer answers:
        "What changed?"

    It does NOT determine whether the change is material.
    That responsibility belongs to the materiality engine.
    """

    def __init__(self, calculator=None):
        self.calculator = calculator or KPICalculator()

    def compare_periods(
        self,
        kpi_name,
        entity_dimension,
        entity_value,
        previous_period,
        current_period,
    ):
        """
        Compare a KPI between two periods for a specific entity.

        Parameters
        ----------
        kpi_name : str
            Registered KPI name.

        entity_dimension : str
            Dimension identifying the entity being analysed.
            Example: "region"

        entity_value : str
            Entity being analysed.
            Example: "Region A"

        previous_period : str
            Earlier reporting period.
            Example: "2026-07"

        current_period : str
            Current reporting period.
            Example: "2026-08"

        Returns
        -------
        dict
            Structured KPI snapshot.
        """

        # --------------------------------------------------
        # Calculate KPI at entity-month level
        # --------------------------------------------------

        result = self.calculator.calculate(
            kpi_name=kpi_name,
            group_by=[
                entity_dimension,
                "month"
            ],
            filters={
                entity_dimension: entity_value
            }
        )

        # --------------------------------------------------
        # Find previous and current period
        # --------------------------------------------------

        previous_rows = result[
            result["month"] == previous_period
        ]

        current_rows = result[
            result["month"] == current_period
        ]

        # --------------------------------------------------
        # Validate periods exist
        # --------------------------------------------------

        if previous_rows.empty:
            raise ValueError(
                f"No data found for {entity_value} "
                f"in previous period {previous_period}."
            )

        if current_rows.empty:
            raise ValueError(
                f"No data found for {entity_value} "
                f"in current period {current_period}."
            )

        # --------------------------------------------------
        # Extract KPI values
        # --------------------------------------------------

        previous_value = float(
            previous_rows.iloc[0][kpi_name]
        )

        current_value = float(
            current_rows.iloc[0][kpi_name]
        )

        # --------------------------------------------------
        # Calculate absolute change
        # --------------------------------------------------

        absolute_change = (
            current_value - previous_value
        )

        # --------------------------------------------------
        # Calculate percentage change
        # --------------------------------------------------

        if previous_value == 0:

            if current_value == 0:
                change_pct = 0.0

            else:
                change_pct = None

        else:

            change_pct = (
                absolute_change / previous_value
            ) * 100

        # --------------------------------------------------
        # Determine direction
        # --------------------------------------------------

        if absolute_change > 0:
            direction = "INCREASE"

        elif absolute_change < 0:
            direction = "DECREASE"

        else:
            direction = "NO_CHANGE"

        # --------------------------------------------------
        # Build snapshot
        # --------------------------------------------------

        snapshot = {
            "kpi": kpi_name,
            "entity_dimension": entity_dimension,
            "entity": entity_value,

            "previous_period": previous_period,
            "current_period": current_period,

            "previous_value": round(
                previous_value,
                2
            ),

            "current_value": round(
                current_value,
                2
            ),

            "absolute_change": round(
                absolute_change,
                2
            ),

            "change_pct": (
                round(change_pct, 2)
                if change_pct is not None
                else None
            ),

            "direction": direction,
        }

        return snapshot