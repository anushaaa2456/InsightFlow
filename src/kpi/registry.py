from pathlib import Path
import yaml


class KPIRegistry:
    """
    Loads and provides access to InsightFlow's KPI semantic definitions.
    """

    def __init__(self, registry_path=None):

        if registry_path is None:
            project_root = Path(__file__).resolve().parents[2]
            registry_path = project_root / "config" / "kpi_registry.yaml"

        self.registry_path = Path(registry_path)

        if not self.registry_path.exists():
            raise FileNotFoundError(
                f"KPI registry not found: {self.registry_path}"
            )

        with open(self.registry_path, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)

        if not self.config or "kpis" not in self.config:
            raise ValueError(
                "Invalid KPI registry: missing 'kpis' section."
            )

        self.kpis = self.config["kpis"]

    def list_kpis(self):
        """Return all registered KPI names."""
        return list(self.kpis.keys())

    def get(self, kpi_name):
        """Return the definition of a specific KPI."""
        if kpi_name not in self.kpis:
            raise KeyError(
                f"KPI '{kpi_name}' is not registered. "
                f"Available KPIs: {self.list_kpis()}"
            )

        return self.kpis[kpi_name]

    def get_calculation(self, kpi_name):
        """Return calculation configuration for a KPI."""
        return self.get(kpi_name)["calculation"]

    def get_drivers(self, kpi_name):
        """Return the driver hierarchy for a KPI."""
        return self.get(kpi_name)["drivers"]

    def get_dimensions(self, kpi_name):
        """Return dimensions available for drill-down."""
        return self.get(kpi_name)["dimensions"]

    def get_materiality_rules(self, kpi_name):
        """Return materiality configuration."""
        return self.get(kpi_name)["materiality"]