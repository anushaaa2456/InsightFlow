from src.evidence.loader import EvidenceLoader
from src.evidence.retriever import EvidenceRetriever
from src.hypothesis.generator import HypothesisGenerator


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


def get_relevant_evidence():

    loader = EvidenceLoader()

    evidence = loader.load_all()

    retriever = EvidenceRetriever(
        evidence
    )

    return retriever.retrieve(
        make_payload()
    )


def test_generator_returns_hypotheses():

    evidence = get_relevant_evidence()

    generator = HypothesisGenerator()

    hypotheses = generator.generate(
        make_payload(),
        evidence,
    )

    assert len(hypotheses) > 0


def test_generated_hypotheses_are_for_primary_driver():

    evidence = get_relevant_evidence()

    generator = HypothesisGenerator()

    hypotheses = generator.generate(
        make_payload(),
        evidence,
    )

    assert all(
        hypothesis.driver == "aov"
        for hypothesis in hypotheses
    )


def test_generated_hypotheses_are_untested():

    evidence = get_relevant_evidence()

    generator = HypothesisGenerator()

    hypotheses = generator.generate(
        make_payload(),
        evidence,
    )

    assert all(
        hypothesis.status == "UNTESTED"
        for hypothesis in hypotheses
    )


def test_aov_hypotheses_include_expected_categories():

    evidence = get_relevant_evidence()

    generator = HypothesisGenerator()

    hypotheses = generator.generate(
        make_payload(),
        evidence,
    )

    ids = {
        hypothesis.hypothesis_id
        for hypothesis in hypotheses
    }

    assert (
        "aov_price_pressure"
        in ids
    )

    assert (
        "aov_premium_mix"
        in ids
    )

    assert (
        "aov_inventory_constraints"
        in ids
    )


def test_hypotheses_have_evidence_ids():

    evidence = get_relevant_evidence()

    generator = HypothesisGenerator()

    hypotheses = generator.generate(
        make_payload(),
        evidence,
    )

    assert all(
        len(
            hypothesis.evidence_ids
        ) > 0
        for hypothesis in hypotheses
    )


def test_generator_does_not_claim_hypotheses_are_supported():

    evidence = get_relevant_evidence()

    generator = HypothesisGenerator()

    hypotheses = generator.generate(
        make_payload(),
        evidence,
    )

    assert all(
        hypothesis.status
        == "UNTESTED"
        for hypothesis in hypotheses
    )


def test_generator_returns_empty_for_unknown_driver():

    generator = HypothesisGenerator()

    payload = make_payload()

    payload["primary_driver"] = {
        "name": "unknown_driver"
    }

    hypotheses = generator.generate(
        payload,
        [],
    )

    assert hypotheses == []

def test_hypothesis_evidence_is_limited():

    evidence = get_relevant_evidence()

    generator = HypothesisGenerator()

    hypotheses = generator.generate(
        make_payload(),
        evidence,
    )

    for hypothesis in hypotheses:

        assert len(
            hypothesis.evidence_ids
        ) <= 10
def test_hypothesis_evidence_is_ranked():

    evidence = get_relevant_evidence()

    generator = HypothesisGenerator()

    hypotheses = generator.generate(
        make_payload(),
        evidence,
    )

    for hypothesis in hypotheses:

        assert len(
            hypothesis.evidence_ids
        ) > 0