from src.kpi.calculator import KPICalculator


def test_revenue_by_region():
    """
    Revenue should be calculable at region level.
    """

    calculator = KPICalculator()

    result = calculator.calculate(
        kpi_name="revenue",
        group_by=["region"]
    )

    assert not result.empty

    assert "region" in result.columns
    assert "revenue" in result.columns

    # Our dataset contains exactly four regions.
    assert len(result) == 4


def test_revenue_by_region_month():
    """
    Revenue should be calculable at region-month level.
    """

    calculator = KPICalculator()

    result = calculator.calculate(
        kpi_name="revenue",
        group_by=[
            "region",
            "month"
        ]
    )

    assert not result.empty

    assert "region" in result.columns
    assert "month" in result.columns
    assert "revenue" in result.columns

    # Four regions × six months.
    assert len(result) == 24


def test_region_filter():
    """
    The calculator should support filtering to a single region.
    """

    calculator = KPICalculator()

    result = calculator.calculate(
        kpi_name="revenue",
        group_by=["region"],
        filters={
            "region": "Region A"
        }
    )

    assert not result.empty

    assert len(result) == 1

    assert result.iloc[0]["region"] == "Region A"


def test_multiple_region_filter():
    """
    The calculator should support filtering to multiple regions.
    """

    calculator = KPICalculator()

    result = calculator.calculate(
        kpi_name="revenue",
        group_by=["region"],
        filters={
            "region": [
                "Region A",
                "Region B"
            ]
        }
    )

    assert not result.empty

    assert set(result["region"]) == {
        "Region A",
        "Region B"
    }


def test_region_a_monthly_revenue():
    """
    Region A should contain six monthly observations.
    """

    calculator = KPICalculator()

    result = calculator.calculate(
        kpi_name="revenue",
        group_by=[
            "region",
            "month"
        ],
        filters={
            "region": "Region A"
        }
    )

    assert len(result) == 6

    assert set(result["region"]) == {
        "Region A"
    }


def test_revenue_values_are_non_negative():
    """
    Revenue should not contain negative aggregated values.
    """

    calculator = KPICalculator()

    result = calculator.calculate(
        kpi_name="revenue",
        group_by=[
            "region",
            "month"
        ]
    )

    assert (result["revenue"] >= 0).all()