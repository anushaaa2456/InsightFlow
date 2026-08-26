from src.investigation.pipeline import (
    InvestigationPipeline,
)


def make_payload():

    return {
        "kpi": "revenue",

        "entity": {
            "dimension": "region",
            "value": "Region A",
        },

        "period": {
            "previous": "2026-07",
            "current": "2026-08",
        },

        "change": {
            "previous_value": 1081001.86,
            "current_value": 1020558.93,
            "absolute_change": -60442.93,
            "change_pct": -5.59,
            "direction": "DECREASE",
        },

        "materiality": {
            "is_material": True,
            "decision": "INVESTIGATE",
        },

        "drivers": [
            {
                "name": "aov",
                "label": "AOV",
                "change_pct": -6.11,
            }
        ],

        "primary_driver": {
            "name": "aov",
            "label": "AOV",
            "change_pct": -6.11,
        },

        "drill_down": [],
    }


def test_investigation_pipeline_runs():

    pipeline = InvestigationPipeline()

    result = pipeline.investigate(
        make_payload()
    )

    assert result is not None

    assert (
        result.kpi
        == "revenue"
    )

    assert (
        result.entity
        == "Region A"
    )


def test_pipeline_retrieves_evidence():

    pipeline = InvestigationPipeline()

    result = pipeline.investigate(
        make_payload()
    )

    assert (
        len(result.evidence)
        > 0
    )

    assert (
        result.metadata[
            "evidence_count"
        ]
        == len(result.evidence)
    )


def test_pipeline_generates_hypotheses():

    pipeline = InvestigationPipeline()

    result = pipeline.investigate(
        make_payload()
    )

    assert (
        len(result.hypotheses)
        > 0
    )

    assert all(
        hypothesis.driver
        == "aov"
        for hypothesis
        in result.hypotheses
    )


def test_pipeline_evaluates_hypotheses():

    pipeline = InvestigationPipeline()

    result = pipeline.investigate(
        make_payload()
    )

    assert all(
        hypothesis.status
        != "UNTESTED"
        for hypothesis
        in result.hypotheses
    )


def test_pipeline_selects_primary_hypothesis():

    pipeline = InvestigationPipeline()

    result = pipeline.investigate(
        make_payload()
    )

    assert (
        result.primary_hypothesis
        is not None
    )

    assert (
        result.primary_hypothesis.driver
        == "aov"
    )


def test_pipeline_result_is_serializable():

    pipeline = InvestigationPipeline()

    result = pipeline.investigate(
        make_payload()
    )

    data = result.to_dict()

    assert isinstance(
        data,
        dict,
    )

    assert (
        data["kpi"]
        == "revenue"
    )

    assert (
        data["entity"]["value"]
        == "Region A"
    )