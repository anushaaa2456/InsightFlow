from src.evidence.loader import EvidenceLoader
from src.evidence.retriever import EvidenceRetriever


def make_revenue_payload():

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
            "change_pct": -5.59,
            "direction": "DECREASE",
        },

        "materiality": {
            "is_material": True,
            "decision": "INVESTIGATE",
        },

        "drivers": [],

        "primary_driver": {
            "name": "aov",
            "label": "AOV",
            "change_pct": -6.11,
        },

        "drill_down": [],
    }


def test_retriever_accepts_analysis_payload():

    loader = EvidenceLoader()

    evidence = loader.load_all()

    retriever = EvidenceRetriever(
        evidence
    )

    payload = make_revenue_payload()

    results = retriever.retrieve(
        payload
    )

    assert len(results) > 0


def test_retriever_prioritizes_region_a():

    loader = EvidenceLoader()

    evidence = loader.load_all()

    retriever = EvidenceRetriever(
        evidence
    )

    payload = make_revenue_payload()

    results = retriever.retrieve(
        payload
    )

    assert all(
        item.relevance >= 0.60
        for item in results
    )

    region_a_results = [
        item
        for item in results
        if item.region == "Region A"
    ]

    assert len(
        region_a_results
    ) > 0


def test_retriever_prioritizes_current_period():

    loader = EvidenceLoader()

    evidence = loader.load_all()

    retriever = EvidenceRetriever(
        evidence
    )

    payload = make_revenue_payload()

    results = retriever.retrieve(
        payload
    )

    current_period_results = [
        item
        for item in results
        if item.period == "2026-08"
    ]

    assert len(
        current_period_results
    ) > 0


def test_retriever_finds_business_context_evidence():

    loader = EvidenceLoader()

    evidence = loader.load_all()

    retriever = EvidenceRetriever(
        evidence
    )

    payload = make_revenue_payload()

    results = retriever.retrieve(
        payload
    )

    categories = {
        item.category
        for item in results
    }

    assert (
        "customer_review"
        in categories
    )

    assert (
        "competitor_news"
        in categories
    )

    assert (
        "sales_note"
        in categories
    )


def test_retriever_finds_inventory_evidence():

    loader = EvidenceLoader()

    evidence = loader.load_all()

    retriever = EvidenceRetriever(
        evidence
    )

    payload = make_revenue_payload()

    results = retriever.retrieve(
        payload
    )

    inventory = [
        item
        for item in results
        if item.category
        == "inventory"
    ]

    assert len(
        inventory
    ) > 0


def test_retriever_assigns_relevance():

    loader = EvidenceLoader()

    evidence = loader.load_all()

    retriever = EvidenceRetriever(
        evidence
    )

    payload = make_revenue_payload()

    results = retriever.retrieve(
        payload
    )

    assert all(
        item.relevance is not None
        for item in results
    )

    assert all(
        0.0
        <= item.relevance
        <= 1.0
        for item in results
    )


def test_retriever_results_are_sorted():

    loader = EvidenceLoader()

    evidence = loader.load_all()

    retriever = EvidenceRetriever(
        evidence
    )

    payload = make_revenue_payload()

    results = retriever.retrieve(
        payload
    )

    scores = [
        item.relevance
        for item in results
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_retrieve_by_category():

    loader = EvidenceLoader()

    evidence = loader.load_all()

    retriever = EvidenceRetriever(
        evidence
    )

    payload = make_revenue_payload()

    grouped = (
        retriever.retrieve_by_category(
            payload
        )
    )

    assert isinstance(
        grouped,
        dict,
    )

    assert (
        "inventory"
        in grouped
    )

    assert (
        "customer_review"
        in grouped
    )
def test_relevance_reasons_are_recorded():

    loader = EvidenceLoader()

    evidence = loader.load_all()

    retriever = EvidenceRetriever(
        evidence
    )

    payload = make_revenue_payload()

    results = retriever.retrieve(
        payload
    )

    assert len(results) > 0

    for item in results:

        assert isinstance(
            item.relevance_reasons,
            list,
        )

        assert len(
            item.relevance_reasons
        ) > 0


def test_region_and_period_are_reflected_in_relevance():

    loader = EvidenceLoader()

    evidence = loader.load_all()

    retriever = EvidenceRetriever(
        evidence
    )

    payload = make_revenue_payload()

    results = retriever.retrieve(
        payload
    )

    strong = [
        item
        for item in results
        if (
            item.region == "Region A"
            and item.period == "2026-08"
        )
    ]

    assert len(strong) > 0

    for item in strong:

        assert (
            "same_region"
            in item.relevance_reasons
        )

        assert (
            "same_period"
            in item.relevance_reasons
        )


def test_relevance_labels():

    assert (
        EvidenceRetriever.relevance_label(
            1.0
        )
        == "HIGH"
    )

    assert (
        EvidenceRetriever.relevance_label(
            0.80
        )
        == "MEDIUM"
    )

    assert (
        EvidenceRetriever.relevance_label(
            0.60
        )
        == "LOW"
    )