import pytest

from src.kpi.calculator import KPICalculator


@pytest.fixture
def calculator():
    return KPICalculator()


# ============================================================
# REVENUE
# ============================================================

def test_revenue_kpi(calculator):

    result = calculator.calculate(
        kpi_name="revenue",
        group_by=["region", "month"]
    )

    assert not result.empty

    assert "region" in result.columns
    assert "month" in result.columns
    assert "revenue" in result.columns

    assert len(result) == 24


# ============================================================
# CUSTOMERS
# ============================================================

def test_customers_kpi(calculator):

    result = calculator.calculate(
        kpi_name="customers",
        group_by=["region", "month"]
    )

    assert not result.empty

    assert "region" in result.columns
    assert "month" in result.columns
    assert "customers" in result.columns

    assert len(result) == 24

    assert (
        result["customers"] > 0
    ).all()


# ============================================================
# ORDERS
# ============================================================

def test_orders_kpi(calculator):

    result = calculator.calculate(
        kpi_name="orders",
        group_by=["region", "month"]
    )

    assert not result.empty

    assert "region" in result.columns
    assert "month" in result.columns
    assert "orders" in result.columns

    assert len(result) == 24

    assert (
        result["orders"] > 0
    ).all()


# ============================================================
# AOV
# ============================================================

def test_aov_kpi(calculator):

    result = calculator.calculate(
        kpi_name="aov",
        group_by=["region", "month"]
    )

    assert not result.empty

    assert "region" in result.columns
    assert "month" in result.columns
    assert "aov" in result.columns

    assert len(result) == 24

    assert (
        result["aov"] > 0
    ).all()


# ============================================================
# INVENTORY AVAILABILITY
# ============================================================

def test_inventory_availability_kpi(calculator):

    result = calculator.calculate(
        kpi_name="inventory_availability",
        group_by=["region", "month"]
    )

    assert not result.empty

    assert "region" in result.columns
    assert "month" in result.columns
    assert "inventory_availability" in result.columns

    assert len(result) == 24

    assert (
        result["inventory_availability"] >= 0
    ).all()

    assert (
        result["inventory_availability"] <= 1
    ).all()


# ============================================================
# KPI RELATIONSHIPS
# ============================================================

def test_aov_matches_revenue_divided_by_orders(
    calculator
):

    revenue = calculator.calculate(
        kpi_name="revenue",
        group_by=["region", "month"]
    )

    orders = calculator.calculate(
        kpi_name="orders",
        group_by=["region", "month"]
    )

    aov = calculator.calculate(
        kpi_name="aov",
        group_by=["region", "month"]
    )

    merged = (
        revenue
        .merge(
            orders,
            on=["region", "month"]
        )
        .merge(
            aov,
            on=["region", "month"]
        )
    )

    expected_aov = (
        merged["revenue"]
        / merged["orders"]
    )

    differences = (
        merged["aov"]
        - expected_aov
    ).abs()

    assert (
        differences < 0.000001
    ).all()


# ============================================================
# REGION A GOLDEN CASE
# ============================================================

def test_region_a_revenue_and_aov(
    calculator
):

    revenue = calculator.calculate(
        kpi_name="revenue",
        group_by=["region", "month"],
        filters={
            "region": "Region A"
        }
    )

    aov = calculator.calculate(
        kpi_name="aov",
        group_by=["region", "month"],
        filters={
            "region": "Region A"
        }
    )

    july_revenue = revenue[
        revenue["month"] == "2026-07"
    ].iloc[0]["revenue"]

    august_revenue = revenue[
        revenue["month"] == "2026-08"
    ].iloc[0]["revenue"]

    july_aov = aov[
        aov["month"] == "2026-07"
    ].iloc[0]["aov"]

    august_aov = aov[
        aov["month"] == "2026-08"
    ].iloc[0]["aov"]

    assert july_revenue == pytest.approx(
        1081001.86,
        abs=0.01
    )

    assert august_revenue == pytest.approx(
        1020558.93,
        abs=0.01
    )

    assert july_aov == pytest.approx(
        165.0888607,
        abs=0.0001
    )

    assert august_aov == pytest.approx(
        155.0059128,
        abs=0.0001
    )