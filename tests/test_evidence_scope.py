from src.evidence.loader import EvidenceLoader
from src.evidence.retriever import EvidenceRetriever


def test_region_scope():

    payload = {
        "kpi": "revenue",

        "entity": {
            "dimension": "region",
            "value": "Region A",
        },

        "period": {
            "previous": "2026-07",
            "current": "2026-08",
        },

        "primary_driver": {
            "name": "aov",
            "label": "AOV",
        },
    }

    evidence = EvidenceLoader().load_all()

    retriever = EvidenceRetriever(
        evidence
    )

    results = retriever.retrieve(
        payload
    )

    for item in results:

        if item.region is not None:

            assert (
                item.region
                == "Region A"
            )
def test_region_a_evidence_is_returned():

    payload = {
        "kpi": "revenue",

        "entity": {
            "dimension": "region",
            "value": "Region A",
        },

        "period": {
            "previous": "2026-07",
            "current": "2026-08",
        },

        "primary_driver": {
            "name": "aov",
            "label": "AOV",
        },
    }

    evidence = EvidenceLoader().load_all()

    retriever = EvidenceRetriever(
        evidence
    )

    results = retriever.retrieve(
        payload
    )

    assert len(results) > 0

    assert any(
        item.region == "Region A"
        for item in results
    )