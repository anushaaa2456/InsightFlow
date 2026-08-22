from src.detection.materiality import MaterialityEngine


def test_large_revenue_decline_is_material():
    """
    A 5.59% decline should trigger materiality because
    it exceeds the configured absolute-change threshold.
    """

    engine = MaterialityEngine()

    result = engine.evaluate(
        kpi_name="revenue",
        change_pct=-5.59
    )

    assert result["signals"]["absolute_change"] is True

    assert result["materiality"] == "MEDIUM"

    assert result["investigate"] is True


def test_small_revenue_change_is_low_materiality():
    """
    A small movement below the configured threshold
    should not trigger investigation by itself.
    """

    engine = MaterialityEngine()

    result = engine.evaluate(
        kpi_name="revenue",
        change_pct=-0.80
    )

    assert result["signals"]["absolute_change"] is False

    assert result["materiality"] == "LOW"

    assert result["investigate"] is False


def test_expected_deviation_increases_materiality():
    """
    A movement that is materially worse than expected
    should trigger the expected-deviation signal.
    """

    engine = MaterialityEngine()

    result = engine.evaluate(
        kpi_name="revenue",
        change_pct=-5.59,
        expected_change_pct=-1.00
    )

    assert result["deviation_from_expected_pct"] == -4.59

    assert result["signals"]["absolute_change"] is True

    assert result["signals"]["expected_deviation"] is True

    assert result["materiality"] == "HIGH"

    assert result["investigate"] is True


def test_peer_context():
    """
    Region A should be identified as materially different
    from its peers.
    """

    engine = MaterialityEngine()

    result = engine.evaluate(
        kpi_name="revenue",
        change_pct=-5.59,
        peer_changes={
            "Region B": 0.47,
            "Region C": 0.45,
            "Region D": -0.88
        }
    )

    assert result["peer_context"] is not None

    assert (
        result["signals"]["peer_outlier"]
        is True
    )

    assert result["investigate"] is True


def test_expected_change_can_be_zero():
    """
    The engine should correctly handle an expected change of zero.
    """

    engine = MaterialityEngine()

    result = engine.evaluate(
        kpi_name="revenue",
        change_pct=4.50,
        expected_change_pct=0.00
    )

    assert result[
        "deviation_from_expected_pct"
    ] == 4.50

    assert result[
        "signals"
    ]["expected_deviation"] is True


def test_positive_change_can_be_material():
    """
    Materiality should work for large positive movements too.
    """

    engine = MaterialityEngine()

    result = engine.evaluate(
        kpi_name="revenue",
        change_pct=6.00
    )

    assert result["signals"]["absolute_change"] is True

    assert result["investigate"] is True