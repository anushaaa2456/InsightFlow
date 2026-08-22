import pytest

from src.kpi.snapshot import KPISnapshot


def test_region_a_july_august_snapshot():
    """
    Region A revenue should decrease from July to August.
    """

    snapshot_engine = KPISnapshot()

    result = snapshot_engine.compare_periods(
        kpi_name="revenue",
        entity_dimension="region",
        entity_value="Region A",
        previous_period="2026-07",
        current_period="2026-08",
    )

    assert result["kpi"] == "revenue"

    assert result["entity_dimension"] == "region"

    assert result["entity"] == "Region A"

    assert result["previous_period"] == "2026-07"

    assert result["current_period"] == "2026-08"

    assert result["previous_value"] == pytest.approx(
        1081001.86,
        abs=0.01
    )

    assert result["current_value"] == pytest.approx(
        1020558.93,
        abs=0.01
    )

    assert result["absolute_change"] == pytest.approx(
        -60442.93,
        abs=0.01
    )

    assert result["change_pct"] == pytest.approx(
        -5.59,
        abs=0.01
    )

    assert result["direction"] == "DECREASE"


def test_region_b_july_august_snapshot():
    """
    Region B revenue should increase from July to August.
    """

    snapshot_engine = KPISnapshot()

    result = snapshot_engine.compare_periods(
        kpi_name="revenue",
        entity_dimension="region",
        entity_value="Region B",
        previous_period="2026-07",
        current_period="2026-08",
    )

    assert result["previous_value"] == pytest.approx(
        1107496.91,
        abs=0.01
    )

    assert result["current_value"] == pytest.approx(
        1112740.61,
        abs=0.01
    )

    assert result["change_pct"] == pytest.approx(
        0.47,
        abs=0.01
    )

    assert result["direction"] == "INCREASE"


def test_no_change_direction():
    """
    The direction logic should correctly identify no change.
    """

    snapshot_engine = KPISnapshot()

    result = snapshot_engine.compare_periods(
        kpi_name="revenue",
        entity_dimension="region",
        entity_value="Region A",
        previous_period="2026-07",
        current_period="2026-07",
    )

    assert result["absolute_change"] == pytest.approx(
        0.0,
        abs=0.01
    )

    assert result["change_pct"] == pytest.approx(
        0.0,
        abs=0.01
    )

    assert result["direction"] == "NO_CHANGE"


def test_invalid_previous_period():
    """
    The engine should fail clearly when the previous period
    does not exist.
    """

    snapshot_engine = KPISnapshot()

    with pytest.raises(ValueError):

        snapshot_engine.compare_periods(
            kpi_name="revenue",
            entity_dimension="region",
            entity_value="Region A",
            previous_period="2025-01",
            current_period="2026-08",
        )


def test_invalid_current_period():
    """
    The engine should fail clearly when the current period
    does not exist.
    """

    snapshot_engine = KPISnapshot()

    with pytest.raises(ValueError):

        snapshot_engine.compare_periods(
            kpi_name="revenue",
            entity_dimension="region",
            entity_value="Region A",
            previous_period="2026-07",
            current_period="2025-01",
        )