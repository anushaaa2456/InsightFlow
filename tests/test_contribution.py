import pytest

from src.drivers.revenue_tree import RevenueDriverTree
from src.drivers.contributions import (
    RevenueContributionEngine
)


def get_region_a_comparison():

    tree = RevenueDriverTree()

    return tree.compare_periods(
        region="Region A",
        previous_period="2026-07",
        current_period="2026-08"
    )


def test_contribution_engine_runs():

    comparison = get_region_a_comparison()

    engine = RevenueContributionEngine()

    result = engine.calculate_contributions(
        comparison
    )

    assert result["region"] == "Region A"

    assert result["previous_period"] == "2026-07"

    assert result["current_period"] == "2026-08"

    assert len(result["drivers"]) == 3


def test_total_revenue_change():

    comparison = get_region_a_comparison()

    engine = RevenueContributionEngine()

    result = engine.calculate_contributions(
        comparison
    )

    assert result[
        "revenue"
    ]["change_pct"] == pytest.approx(
        -5.5913807586,
        abs=0.01
    )


def test_all_top_level_drivers_present():

    comparison = get_region_a_comparison()

    engine = RevenueContributionEngine()

    result = engine.calculate_contributions(
        comparison
    )

    driver_names = {
        driver["name"]
        for driver in result["drivers"]
    }

    assert driver_names == {
        "active_customers",
        "orders_per_customer",
        "aov",
    }


def test_contributions_sum_to_revenue_change():

    comparison = get_region_a_comparison()

    engine = RevenueContributionEngine()

    result = engine.calculate_contributions(
        comparison
    )

    contribution_total = sum(
        driver["contribution_pp"]
        for driver in result["drivers"]
    )

    assert contribution_total == pytest.approx(
        result["revenue"]["change_pct"],
        abs=0.0001
    )


def test_aov_is_primary_driver():

    comparison = get_region_a_comparison()

    engine = RevenueContributionEngine()

    result = engine.calculate_contributions(
        comparison
    )

    assert result[
        "primary_driver"
    ]["name"] == "aov"


def test_aov_has_negative_contribution():

    comparison = get_region_a_comparison()

    engine = RevenueContributionEngine()

    result = engine.calculate_contributions(
        comparison
    )

    aov = next(
        driver
        for driver in result["drivers"]
        if driver["name"] == "aov"
    )

    assert aov["change_pct"] < 0

    assert aov["contribution_pp"] < 0


def test_customer_and_frequency_are_not_primary():

    comparison = get_region_a_comparison()

    engine = RevenueContributionEngine()

    result = engine.calculate_contributions(
        comparison
    )

    primary = result[
        "primary_driver"
    ]["name"]

    assert primary == "aov"