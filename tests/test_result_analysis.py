from src.analysis.insight_pipeline import (
    InsightPipeline
)

from src.analysis.result import (
    AnalysisResult
)


def test_pipeline_returns_analysis_result():

    pipeline = InsightPipeline()

    result = pipeline.analyze(
        kpi_name="revenue",
        entity_dimension="region",
        entity_value="Region A",
        previous_period="2026-07",
        current_period="2026-08",
    )

    assert isinstance(
        result,
        AnalysisResult
    )


def test_analysis_result_has_expected_structure():

    pipeline = InsightPipeline()

    result = pipeline.analyze(
        kpi_name="revenue",
        entity_dimension="region",
        entity_value="Region A",
        previous_period="2026-07",
        current_period="2026-08",
    )

    output = result.to_dict()

    assert output["kpi"] == "revenue"

    assert output["entity"] == {
        "dimension": "region",
        "value": "Region A",
    }

    assert output["period"] == {
        "previous": "2026-07",
        "current": "2026-08",
    }

    assert (
        output["change"]["change_pct"]
        == -5.59
    )

    assert (
        output["materiality"]["is_material"]
        is True
    )


def test_primary_driver_is_aov():

    pipeline = InsightPipeline()

    result = pipeline.analyze(
        kpi_name="revenue",
        entity_dimension="region",
        entity_value="Region A",
        previous_period="2026-07",
        current_period="2026-08",
    )

    assert result.primary_driver is not None

    assert (
        result.primary_driver.name
        == "aov"
    )

    assert (
        result.primary_driver.label
        == "AOV"
    )


def test_driver_results_are_structured():

    pipeline = InsightPipeline()

    result = pipeline.analyze(
        kpi_name="revenue",
        entity_dimension="region",
        entity_value="Region A",
        previous_period="2026-07",
        current_period="2026-08",
    )

    assert len(result.drivers) == 3

    for driver in result.drivers:

        assert driver.name
        assert driver.label

        assert (
            driver.change_pct
            is not None
        )

        assert (
            driver.contribution_pp
            is not None
        )


def test_evidence_payload_contains_only_analytical_facts():

    pipeline = InsightPipeline()

    result = pipeline.analyze(
        kpi_name="revenue",
        entity_dimension="region",
        entity_value="Region A",
        previous_period="2026-07",
        current_period="2026-08",
    )

    payload = (
        result.to_evidence_payload()
    )

    assert payload["kpi"] == "revenue"

    assert payload["change"]["change_pct"] == -5.59

    assert (
        payload["primary_driver"]["name"]
        == "aov"
    )

    # The analytical layer must NOT invent
    # causal explanations.

    assert "hypothesis" not in payload

    assert "cause" not in payload

    assert "explanation" not in payload


def test_result_is_json_serializable():

    import json

    pipeline = InsightPipeline()

    result = pipeline.analyze(
        kpi_name="revenue",
        entity_dimension="region",
        entity_value="Region A",
        previous_period="2026-07",
        current_period="2026-08",
    )

    output = result.to_dict()

    serialized = json.dumps(
        output
    )

    assert isinstance(
        serialized,
        str
    )