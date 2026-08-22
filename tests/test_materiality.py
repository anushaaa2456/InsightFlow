from src.detection.materiality import (
    MaterialityEngine
)


def test_material_change():

    engine = MaterialityEngine()

    result = engine.evaluate(
        kpi_name="revenue",
        change_pct=-5.59
    )

    assert result["is_material"] is True

    assert result["decision"] == (
        "INVESTIGATE"
    )


def test_small_change_is_not_material():

    engine = MaterialityEngine()

    result = engine.evaluate(
        kpi_name="revenue",
        change_pct=-1.5
    )

    assert result["is_material"] is False

    assert result["decision"] == (
        "NO_INVESTIGATION"
    )


def test_expected_deviation_triggers_investigation():

    engine = MaterialityEngine()

    result = engine.evaluate(
        kpi_name="revenue",
        change_pct=-8.0,
        expected_change_pct=-1.0
    )

    assert result["is_material"] is True

    assert result["decision"] == (
        "INVESTIGATE"
    )


def test_change_below_threshold_but_expected_deviation_is_material():

    engine = MaterialityEngine()

    result = engine.evaluate(
        kpi_name="revenue",
        change_pct=-2.5,
        expected_change_pct=0.0
    )

    assert result["period_change"]["is_material"] is False

    assert (
        result["expected_deviation"]["is_material"]
        is True
    )

    assert result["is_material"] is True


def test_expected_deviation_can_be_non_material():

    engine = MaterialityEngine()

    result = engine.evaluate(
        kpi_name="revenue",
        change_pct=-2.5,
        expected_change_pct=-1.5
    )

    assert result["period_change"]["is_material"] is False

    assert (
        result["expected_deviation"]["is_material"]
        is False
    )

    assert result["is_material"] is False