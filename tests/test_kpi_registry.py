from src.kpi.registry import KPIRegistry


def test_registry_loads():

    registry = KPIRegistry()

    assert "revenue" in registry.list_kpis()


def test_revenue_definition():

    registry = KPIRegistry()

    revenue = registry.get("revenue")

    assert revenue["name"] == "Revenue"
    assert revenue["calculation"]["method"] == "sum"
    assert revenue["calculation"]["column"] == "revenue"


def test_revenue_drivers():

    registry = KPIRegistry()

    drivers = registry.get_drivers("revenue")

    assert "customers" in drivers
    assert "orders_per_customer" in drivers
    assert "aov" in drivers


def test_revenue_dimensions():

    registry = KPIRegistry()

    dimensions = registry.get_dimensions("revenue")

    assert "region" in dimensions
    assert "product" in dimensions
    assert "channel" in dimensions