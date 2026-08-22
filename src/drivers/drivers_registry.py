from src.kpi.registry import KPIRegistry


class DriverRegistry:
    """
    Provides structured access to KPI driver hierarchies.

    The KPI registry remains the single source of truth.
    This class provides a clean analytical interface over
    the driver definitions.
    """

    def __init__(self, registry=None):
        self.registry = registry or KPIRegistry()

    # ==========================================================
    # KPI DRIVERS
    # ==========================================================

    def get_drivers(self, kpi_name):
        """
        Return the first-level drivers for a KPI.

        Example:

            revenue
            ->
            [
                "customers",
                "orders_per_customer",
                "aov"
            ]
        """

        drivers = self.registry.get_drivers(
            kpi_name
        )

        return list(drivers.keys())

    # ==========================================================
    # DRIVER CONFIGURATION
    # ==========================================================

    def get_driver(
        self,
        kpi_name,
        driver_name
    ):
        """
        Return the complete configuration of
        a specific driver.
        """

        drivers = self.registry.get_drivers(
            kpi_name
        )

        if driver_name not in drivers:

            raise KeyError(
                f"Driver '{driver_name}' "
                f"is not registered for KPI "
                f"'{kpi_name}'. "
                f"Available drivers: "
                f"{list(drivers.keys())}"
            )

        return drivers[driver_name]

    # ==========================================================
    # SUB-DRIVERS
    # ==========================================================

    def get_sub_drivers(
        self,
        kpi_name,
        driver_name
    ):
        """
        Return the sub-drivers of a first-level driver.

        Example:

            revenue -> aov

            returns:

            [
                "price",
                "discounting",
                "product_mix",
                "attach_rate"
            ]
        """

        driver = self.get_driver(
            kpi_name,
            driver_name
        )

        return driver.get(
            "sub_drivers",
            []
        )

    # ==========================================================
    # DRIVER FORMULA
    # ==========================================================

    def get_driver_formula(
        self,
        kpi_name,
        driver_name
    ):
        """
        Return the formula associated with a driver.
        """

        driver = self.get_driver(
            kpi_name,
            driver_name
        )

        return driver.get(
            "formula"
        )

    # ==========================================================
    # DRIVER TREE
    # ==========================================================

    def get_driver_tree(
        self,
        kpi_name
    ):
        """
        Return the complete driver hierarchy for a KPI.

        Output structure:

        {
            driver_name: {
                "formula": ...,
                "sub_drivers": [...]
            }
        }
        """

        drivers = self.registry.get_drivers(
            kpi_name
        )

        tree = {}

        for driver_name, config in drivers.items():

            tree[driver_name] = {
                "formula": config.get(
                    "formula"
                ),
                "sub_drivers": config.get(
                    "sub_drivers",
                    []
                )
            }

        return tree

    # ==========================================================
    # DRIVER EXISTENCE
    # ==========================================================

    def has_driver(
        self,
        kpi_name,
        driver_name
    ):
        """
        Check whether a driver exists for a KPI.
        """

        drivers = self.registry.get_drivers(
            kpi_name
        )

        return driver_name in drivers

    # ==========================================================
    # SUB-DRIVER EXISTENCE
    # ==========================================================

    def has_sub_driver(
        self,
        kpi_name,
        driver_name,
        sub_driver_name
    ):
        """
        Check whether a sub-driver exists.
        """

        return (
            sub_driver_name
            in self.get_sub_drivers(
                kpi_name,
                driver_name
            )
        )