import json

from src.evidence.models import Evidence
from src.hypothesis.models import Hypothesis
from src.investigation.result import (
    InvestigationResult,
)


def make_evidence():

    return Evidence(
        evidence_id="evidence_1",
        source_type="unstructured",
        source="business_context.json",
        category="competitor_news",
        text=(
            "Competitor X reduced prices "
            "on comparable premium products."
        ),
        period="2026-08",
        region="Region A",
    )


def make_hypothesis():

    return Hypothesis(
        hypothesis_id="aov_price_pressure",
        statement=(
            "Price changes contributed "
            "to the AOV change."
        ),
        driver="aov",
        evidence_ids=[
            "evidence_1"
        ],
        supporting_evidence_ids=[
            "evidence_1"
        ],
        confidence="LOW",
        confidence_score=1.0,
        status="PARTIALLY_SUPPORTED",
    )


def make_result():

    return InvestigationResult(
        kpi="revenue",
        entity_dimension="region",
        entity="Region A",
        previous_period="2026-07",
        current_period="2026-08",
        primary_driver="aov",
        evidence=[
            make_evidence()
        ],
        hypotheses=[
            make_hypothesis()
        ],
        primary_hypothesis=(
            make_hypothesis()
        ),
    )


def test_investigation_result():

    result = make_result()

    assert (
        result.kpi
        == "revenue"
    )

    assert (
        result.entity
        == "Region A"
    )

    assert (
        result.primary_driver
        == "aov"
    )

    assert len(
        result.evidence
    ) == 1

    assert len(
        result.hypotheses
    ) == 1


def test_investigation_result_serialization():

    result = make_result()

    data = result.to_dict()

    json.dumps(data)

    assert (
        data["kpi"]
        == "revenue"
    )

    assert (
        data["entity"]["value"]
        == "Region A"
    )

    assert (
        data["primary_driver"]
        == "aov"
    )

    assert len(
        data["evidence"]
    ) == 1

    assert len(
        data["hypotheses"]
    ) == 1


def test_primary_hypothesis_serialization():

    result = make_result()

    data = result.to_dict()

    assert (
        data["primary_hypothesis"]
        is not None
    )

    assert (
        data["primary_hypothesis"][
            "hypothesis_id"
        ]
        == "aov_price_pressure"
    )