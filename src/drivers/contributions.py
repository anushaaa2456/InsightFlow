import math


class RevenueContributionEngine:
    """
    Attributes the observed revenue movement across the
    multiplicative revenue drivers:

        Revenue =
        Active Customers
        × Orders per Customer
        × AOV

    Uses log-change decomposition so that driver contributions
    are additive and interaction effects are handled consistently.

    Important:
    This engine attributes contribution. It does not determine
    causality.
    """

    DRIVER_LABELS = {
        "active_customers": "Active Customers",
        "orders_per_customer": "Orders per Customer",
        "aov": "AOV",
    }

    def __init__(self):
        self.drivers = [
            "active_customers",
            "orders_per_customer",
            "aov",
        ]

    def _log_change(self, previous, current):
        """
        Calculate log change between two positive values.
        """

        if previous <= 0 or current <= 0:
            raise ValueError(
                "Log-change decomposition requires "
                "positive driver values."
            )

        return math.log(current / previous)

    def calculate_contributions(self, comparison):
        """
        Calculate driver contributions from a RevenueDriverTree
        period comparison.

        Parameters
        ----------
        comparison : dict
            Output from RevenueDriverTree.compare_periods().

        Returns
        -------
        dict
            Driver-level contribution analysis.
        """

        previous = comparison["previous"]
        current = comparison["current"]

        previous_revenue = previous["revenue"]
        current_revenue = current["revenue"]

        # --------------------------------------------------
        # Total revenue change
        # --------------------------------------------------

        revenue_change_pct = (
            (current_revenue - previous_revenue)
            / previous_revenue
        ) * 100

        total_log_change = self._log_change(
            previous_revenue,
            current_revenue
        )

        # --------------------------------------------------
        # Calculate individual log changes
        # --------------------------------------------------

        log_changes = {}

        for driver in self.drivers:

            log_changes[driver] = self._log_change(
                previous[driver],
                current[driver]
            )

        # --------------------------------------------------
        # Convert each log contribution into an approximate
        # percentage-point contribution to the observed
        # revenue change.
        #
        # Contribution share =
        # driver log change / total log change
        #
        # Contribution pp =
        # share × observed revenue change
        # --------------------------------------------------

        drivers = []

        for driver in self.drivers:

            driver_log_change = log_changes[driver]

            if abs(total_log_change) < 1e-12:

                contribution_share = 0.0
                contribution_pp = 0.0

            else:

                contribution_share = (
                    driver_log_change
                    / total_log_change
                )

                contribution_pp = (
                    contribution_share
                    * revenue_change_pct
                )

            driver_change_pct = (
                (
                    current[driver]
                    - previous[driver]
                )
                / previous[driver]
            ) * 100

            drivers.append({
                "name": driver,

                "label": self.DRIVER_LABELS[
                    driver
                ],

                "previous_value": previous[
                    driver
                ],

                "current_value": current[
                    driver
                ],

                "change_pct": driver_change_pct,

                "log_change": driver_log_change,

                "contribution_share": contribution_share,

                "contribution_pp": contribution_pp,
            })

        # --------------------------------------------------
        # Rank drivers by absolute contribution
        # --------------------------------------------------

        drivers.sort(
            key=lambda x: abs(
                x["contribution_pp"]
            ),
            reverse=True
        )

        # --------------------------------------------------
        # Add ranking
        # --------------------------------------------------

        for rank, driver in enumerate(
            drivers,
            start=1
        ):
            driver["rank"] = rank

        # --------------------------------------------------
        # Primary driver
        # --------------------------------------------------

        primary_driver = drivers[0]

        # --------------------------------------------------
        # Build result
        # --------------------------------------------------

        return {
            "region": comparison["region"],

            "previous_period": comparison[
                "previous_period"
            ],

            "current_period": comparison[
                "current_period"
            ],

            "revenue": {
                "previous_value": previous_revenue,
                "current_value": current_revenue,
                "change_pct": revenue_change_pct,
                "log_change": total_log_change,
            },

            "drivers": drivers,

            "primary_driver": {
                "name": primary_driver["name"],
                "label": primary_driver["label"],
                "contribution_pp": primary_driver[
                    "contribution_pp"
                ],
            },
        }