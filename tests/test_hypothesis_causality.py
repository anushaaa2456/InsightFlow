from src.hypothesis.evaluator import HypothesisEvaluator
from src.hypothesis.models import Hypothesis


class FakeEvidence:

    def __init__(
        self,
        evidence_id,
        category,
        metadata=None,
    ):
        self.evidence_id = evidence_id
        self.category = category
        self.metadata = metadata or {}


def make_inventory_hypothesis():

    return Hypothesis(
        hypothesis_id="aov_inventory_constraints",
        driver="aov",
        statement=(
            "Inventory constraints contributed "
            "to the AOV change."
        ),
        evidence_ids=[
            "e1",
            "e2",
        ],
        metadata={
            "candidate_category":
                "inventory_constraints"
        },
    )


def test_inventory_evidence_supports_inventory_hypothesis():

    hypothesis = (
        make_inventory_hypothesis()
    )

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

    result = (
        HypothesisEvaluator()
        .evaluate(
            hypothesis,
            evidence,
        )
    )

    assert (
        result.status
        == "SUPPORTED"
    )

    assert (
        result.confidence
        == "HIGH"
    )