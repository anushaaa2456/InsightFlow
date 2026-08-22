from pathlib import Path

import pandas as pd

from src.kpi.registry import KPIRegistry


class RevenueDriverTree:
    """
    Calculates the top-level MECE revenue drivers.

    Revenue is decomposed as:

        Revenue
            =
        Active Customers
        × Orders per Customer
        × AOV

    This module calculates the underlying metrics.
    Contribution attribution is handled separately.
    """

    def __init__(self, registry=None):
        self.registry = registry or KPIRegistry()

    def load_data(self):
        """
        Load transaction data from the configured source.
        """

        kpi_config = self.registry.get("revenue")

        relative_path = kpi_config["data_source"]["file"]

        project_root = Path(__file__).resolve().parents[2]

        data_path = project_root / relative_path

        if not data_path.exists():
            raise FileNotFoundError(
                f"Revenue data file not found: {data_path}"
            )

        df = pd.read_csv(data_path)

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

        return df

    def calculate_period_metrics(
        self,
        region,
        period
    ):
        """
        Calculate top-level revenue driver metrics
        for one region and one month.
        """

        df = self.load_data()

        # --------------------------------------------------
        # Create reporting month
        # --------------------------------------------------

        df["month"] = (
            df["date"]
            .dt.to_period("M")
            .astype(str)
        )

        # --------------------------------------------------
        # Filter region and period
        # --------------------------------------------------

        filtered = df[
            (df["region"] == region)
            &
            (df["month"] == period)
        ].copy()

        if filtered.empty:
            raise ValueError(
                f"No transaction data found for "
                f"{region} in {period}."
            )

        # --------------------------------------------------
        # Revenue
        # --------------------------------------------------

        revenue = float(
            filtered["revenue"].sum()
        )

        # --------------------------------------------------
        # Active customers
        # --------------------------------------------------

        active_customers = int(
            filtered["customer_id"].nunique()
        )

        # --------------------------------------------------
        # Orders
        # --------------------------------------------------

        orders = float(
            filtered["orders"].sum()
        )

        # --------------------------------------------------
        # Orders per customer
        # --------------------------------------------------

        if active_customers == 0:
            orders_per_customer = 0.0

        else:
            orders_per_customer = (
                orders / active_customers
            )

        # --------------------------------------------------
        # Average order value
        # --------------------------------------------------

        if orders == 0:
            aov = 0.0

        else:
            aov = revenue / orders

        # --------------------------------------------------
        # Validate revenue identity
        #
        # Use FULL-PRECISION values here.
        # Do not use rounded presentation values.
        # --------------------------------------------------

        reconstructed_revenue = (
            active_customers
            * orders_per_customer
            * aov
        )

        if abs(
            reconstructed_revenue - revenue
        ) > 0.01:

            raise ValueError(
                "Revenue decomposition identity failed. "
                "Check customer, order or revenue calculations."
            )

        # --------------------------------------------------
        # Return metrics
        #
        # Keep full precision internally.
        # Formatting/rounding belongs to presentation.
        # --------------------------------------------------

        return {
            "region": region,
            "period": period,

            "revenue": revenue,

            "active_customers": active_customers,

            "orders": orders,

            "orders_per_customer": orders_per_customer,

            "aov": aov,
        }

    def compare_periods(
        self,
        region,
        previous_period,
        current_period
    ):
        """
        Compare top-level revenue drivers between
        two periods.

        Returns both period values and percentage changes.
        """

        previous = self.calculate_period_metrics(
            region=region,
            period=previous_period
        )

        current = self.calculate_period_metrics(
            region=region,
            period=current_period
        )

        def pct_change(
            previous_value,
            current_value
        ):

            if previous_value == 0:

                if current_value == 0:
                    return 0.0

                return None

            return (
                (
                    current_value
                    - previous_value
                )
                / previous_value
            ) * 100

        comparison = {
            "region": region,

            "previous_period": previous_period,

            "current_period": current_period,

            "previous": previous,

            "current": current,

            "changes": {

                "revenue": pct_change(
                    previous["revenue"],
                    current["revenue"]
                ),

                "active_customers": pct_change(
                    previous["active_customers"],
                    current["active_customers"]
                ),

                "orders_per_customer": pct_change(
                    previous["orders_per_customer"],
                    current["orders_per_customer"]
                ),

                "aov": pct_change(
                    previous["aov"],
                    current["aov"]
                ),
            }
        }

        return comparison