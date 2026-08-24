from dataclasses import dataclass

from src.hypothesis.evaluator import (
    HypothesisEvaluator,
)
from src.hypothesis.models import Hypothesis


@dataclass
class FakeEvidence:

    evidence_id: str
    category: str
    metadata: dict | None = None

    def __post_init__(self):

        if self.metadata is None:
            self.metadata = {}


def make_hypothesis():

    return Hypothesis(
        hypothesis_id="aov_inventory",
        statement=(
            "Inventory constraints contributed "
            "to the AOV change."
        ),
        driver="aov",
        evidence_ids=[
            "e1",
            "e2",
        ],
        metadata={
            "candidate_category":
                "inventory_constraints"
        },
    )


def test_supported_hypothesis():

    hypothesis = make_hypothesis()

    evidence = [
        FakeEvidence(
            evidence_id="e1",
            category="inventory",
        ),
        FakeEvidence(
            evidence_id="e2",
            category="stockout",
        ),
    ]

    evaluator = HypothesisEvaluator()

    result = evaluator.evaluate(
        hypothesis,
        evidence,
    )

    assert (
        result.status
        == "SUPPORTED"
    )

    assert len(
        result.supporting_evidence_ids
    ) == 2

    assert (
        result.contradicting_evidence_ids
        == []
    )


def test_partially_supported_hypothesis():

    hypothesis = make_hypothesis()

    hypothesis.evidence_ids = [
        "e1"
    ]

    evidence = [
        FakeEvidence(
            evidence_id="e1",
            category="inventory",
        )
    ]

    evaluator = HypothesisEvaluator()

    result = evaluator.evaluate(
        hypothesis,
        evidence,
    )

    assert (
        result.status
        == "PARTIALLY_SUPPORTED"
    )

    assert (
        result.confidence
        == "LOW"
    )


def test_insufficient_evidence():

    hypothesis = make_hypothesis()

    hypothesis.evidence_ids = [
        "missing"
    ]

    evaluator = HypothesisEvaluator()

    result = evaluator.evaluate(
        hypothesis,
        [],
    )

    assert (
        result.status
        == "INSUFFICIENT_EVIDENCE"
    )

    assert (
        result.confidence_score
        == 0.0
    )


def test_contradicting_evidence():

    hypothesis = make_hypothesis()

    hypothesis.evidence_ids = [
        "e1",
        "e2",
    ]

    evidence = [
        FakeEvidence(
            evidence_id="e1",
            category="inventory",
        ),
        FakeEvidence(
            evidence_id="e2",
            category="inventory",
            metadata={
                "contradicts_hypothesis":
                    True
            },
        ),
    ]

    evaluator = HypothesisEvaluator()

    result = evaluator.evaluate(
        hypothesis,
        evidence,
    )

    assert (
        result.status
        == "PARTIALLY_SUPPORTED"
    )

    assert (
        result.confidence_score
        == 0.5
    )

    assert (
        "e1"
        in result.supporting_evidence_ids
    )

    assert (
        "e2"
        in result.contradicting_evidence_ids
    )


def test_high_confidence():

    hypothesis = make_hypothesis()

    hypothesis.evidence_ids = [
        "e1",
        "e2",
        "e3",
    ]

    evidence = [
        FakeEvidence(
            evidence_id="e1",
            category="inventory",
        ),
        FakeEvidence(
            evidence_id="e2",
            category="stockout",
        ),
        FakeEvidence(
            evidence_id="e3",
            category="inventory",
        ),
    ]

    evaluator = HypothesisEvaluator()

    result = evaluator.evaluate(
        hypothesis,
        evidence,
    )

    assert (
        result.status
        == "SUPPORTED"
    )

    assert (
        result.confidence
        == "HIGH"
    )

    assert (
        result.confidence_score
        == 1.0
    )