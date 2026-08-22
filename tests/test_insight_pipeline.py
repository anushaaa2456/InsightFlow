import pytest

from src.analysis.insight_pipeline import (
    InsightPipeline
)


@pytest.fixture
def pipeline():
    return InsightPipeline()


# ============================================================
# MATERIAL REVENUE CHANGE
# ============================================================

def test_material_revenue_change(
    pipeline
):

    result = pipeline.analyze(
        kpi_name="revenue",
        entity_dimension="region",
        entity_value="Region A",
        previous_period="2026-07",
        current_period="2026-08",
    )

    assert result["kpi"] == "revenue"

    assert result["entity"] == "Region A"

    assert (
        result["snapshot"]["change_pct"]
        == pytest.approx(
            -5.59,
            abs=0.01
        )
    )

    assert (
        result["materiality"]["is_material"]
        is True
    )

    assert (
        result["decision"]
        == "INVESTIGATE"
    )


# ============================================================
# PRIMARY DRIVER
# ============================================================

def test_revenue_primary_driver(
    pipeline
):

    result = pipeline.analyze(
        kpi_name="revenue",
        entity_dimension="region",
        entity_value="Region A",
        previous_period="2026-07",
        current_period="2026-08",
    )

    assert (
        result["primary_driver"]["name"]
        == "aov"
    )


# ============================================================
# DRIVER CONTRIBUTION
# ============================================================

def test_revenue_driver_contribution(
    pipeline
):

    result = pipeline.analyze(
        kpi_name="revenue",
        entity_dimension="region",
        entity_value="Region A",
        previous_period="2026-07",
        current_period="2026-08",
    )

    drivers = result["drivers"]

    assert len(drivers) == 3

    total_contribution = sum(
        driver["contribution_pp"]
        for driver in drivers
    )

    assert total_contribution == pytest.approx(
        -5.5913807586,
        abs=0.0001
    )


# ============================================================
# AOV CONTRIBUTION
# ============================================================

def test_aov_contribution(
    pipeline
):

    result = pipeline.analyze(
        kpi_name="revenue",
        entity_dimension="region",
        entity_value="Region A",
        previous_period="2026-07",
        current_period="2026-08",
    )

    aov = next(
        driver
        for driver in result["drivers"]
        if driver["name"] == "aov"
    )

    assert (
        aov["contribution_pp"]
        < 0
    )


# ============================================================
# NON-MATERIAL MOVEMENT
# ============================================================

def test_non_material_change_stops_investigation(
    pipeline
):

    # Revenue threshold = 3%.
    # This change should not trigger investigation.

    result = pipeline.materiality.evaluate(
        kpi_name="revenue",
        change_pct=-1.0,
    )

    assert (
        result["is_material"]
        is False
    )

    assert (
        result["decision"]
        == "NO_INVESTIGATION"
    )


# ============================================================
# EXPECTED-VALUE DEVIATION
# ============================================================

def test_expected_deviation_triggers_investigation(
    pipeline
):

    result = pipeline.analyze(
        kpi_name="revenue",
        entity_dimension="region",
        entity_value="Region A",
        previous_period="2026-07",
        current_period="2026-08",
        expected_change_pct=-1.0,
    )

    assert (
        result["materiality"]["is_material"]
        is True
    )

    assert (
        result["decision"]
        == "INVESTIGATE"
    )