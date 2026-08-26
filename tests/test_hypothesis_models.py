import json

import pytest

from src.hypothesis.models import Hypothesis


def test_create_hypothesis():

    hypothesis = Hypothesis(
        hypothesis_id="aov_premium_mix",
        statement=(
            "Premium product mix decline "
            "contributed to the AOV decline."
        ),
        driver="aov",
    )

    assert (
        hypothesis.hypothesis_id
        == "aov_premium_mix"
    )

    assert (
        hypothesis.driver
        == "aov"
    )

    assert (
        hypothesis.status
        == "UNTESTED"
    )

    assert (
        hypothesis.supporting_evidence_ids
        == []
    )

    assert (
        hypothesis.contradicting_evidence_ids
        == []
    )


def test_hypothesis_with_evidence():

    hypothesis = Hypothesis(
        hypothesis_id="inventory_aov",
        statement=(
            "Premium inventory constraints "
            "contributed to the AOV decline."
        ),
        driver="aov",
        evidence_ids=[
            "context_0",
            "operation_123",
        ],
        supporting_evidence_ids=[
            "context_0",
            "operation_123",
        ],
    )

    assert len(
        hypothesis.evidence_ids
    ) == 2

    assert len(
        hypothesis.supporting_evidence_ids
    ) == 2


def test_hypothesis_status_validation():

    hypothesis = Hypothesis(
        hypothesis_id="test",
        statement="Test hypothesis",
        driver="aov",
        status="SUPPORTED",
    )

    assert (
        hypothesis.status
        == "SUPPORTED"
    )


def test_invalid_hypothesis_status():

    with pytest.raises(ValueError):

        Hypothesis(
            hypothesis_id="test",
            statement="Test hypothesis",
            driver="aov",
            status="RANDOM_STATUS",
        )


def test_empty_hypothesis_id():

    with pytest.raises(ValueError):

        Hypothesis(
            hypothesis_id="",
            statement="Test hypothesis",
            driver="aov",
        )


def test_empty_statement():

    with pytest.raises(ValueError):

        Hypothesis(
            hypothesis_id="test",
            statement="",
            driver="aov",
        )


def test_hypothesis_serialization():

    hypothesis = Hypothesis(
        hypothesis_id="test",
        statement="Test hypothesis",
        driver="aov",
        supporting_evidence_ids=[
            "evidence_1"
        ],
        confidence="HIGH",
        confidence_score=0.85,
        status="SUPPORTED",
        reasoning=(
            "Multiple aligned pieces "
            "of evidence support this hypothesis."
        ),
    )

    result = hypothesis.to_dict()

    json.dumps(result)

    assert (
        result["hypothesis_id"]
        == "test"
    )

    assert (
        result["confidence"]
        == "HIGH"
    )

    assert (
        result["status"]
        == "SUPPORTED"
    )


def test_hypothesis_from_dict():

    original = Hypothesis(
        hypothesis_id="test",
        statement="Test hypothesis",
        driver="aov",
        status="SUPPORTED",
    )

    restored = Hypothesis.from_dict(
        original.to_dict()
    )

    assert (
        restored.hypothesis_id
        == original.hypothesis_id
    )

    assert (
        restored.statement
        == original.statement
    )

    assert (
        restored.driver
        == original.driver
    )

    assert (
        restored.status
        == original.status
    )