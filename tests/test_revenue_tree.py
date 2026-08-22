import pytest

from src.drivers.revenue_tree import RevenueDriverTree


def test_region_a_july_metrics():

    engine = RevenueDriverTree()

    result = engine.calculate_period_metrics(
        region="Region A",
        period="2026-07"
    )

    assert result["region"] == "Region A"

    assert result["period"] == "2026-07"

    assert result["revenue"] == pytest.approx(
        1081001.86,
        abs=0.01
    )

    assert result["active_customers"] > 0

    assert result["orders"] > 0

    assert result["orders_per_customer"] > 0

    assert result["aov"] > 0


def test_region_a_august_metrics():

    engine = RevenueDriverTree()

    result = engine.calculate_period_metrics(
        region="Region A",
        period="2026-08"
    )

    assert result["region"] == "Region A"

    assert result["period"] == "2026-08"

    assert result["revenue"] == pytest.approx(
        1020558.93,
        abs=0.01
    )

    assert result["active_customers"] > 0

    assert result["orders"] > 0

    assert result["orders_per_customer"] > 0

    assert result["aov"] > 0


def test_revenue_identity():

    engine = RevenueDriverTree()

    result = engine.calculate_period_metrics(
        region="Region A",
        period="2026-08"
    )

    reconstructed_revenue = (
        result["active_customers"]
        * result["orders_per_customer"]
        * result["aov"]
    )

    assert reconstructed_revenue == pytest.approx(
        result["revenue"],
        abs=0.01
    )


def test_period_comparison():

    engine = RevenueDriverTree()

    result = engine.compare_periods(
        region="Region A",
        previous_period="2026-07",
        current_period="2026-08"
    )

    assert result["region"] == "Region A"

    assert result["previous_period"] == "2026-07"

    assert result["current_period"] == "2026-08"

    assert result["changes"]["revenue"] == pytest.approx(
        -5.59,
        abs=0.01
    )


def test_driver_changes_are_present():

    engine = RevenueDriverTree()

    result = engine.compare_periods(
        region="Region A",
        previous_period="2026-07",
        current_period="2026-08"
    )

    changes = result["changes"]

    assert "active_customers" in changes

    assert "orders_per_customer" in changes

    assert "aov" in changes