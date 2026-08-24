from src.evidence.loader import EvidenceLoader


def test_load_transactions():

    loader = EvidenceLoader()

    evidence = loader.load_transactions()

    assert len(evidence) > 0

    first = evidence[0]

    assert (
        first.source_type
        == "structured"
    )

    assert (
        first.source
        == "transactions.csv"
    )

    assert (
        first.category
        == "transaction"
    )

    assert first.value is not None

    assert first.region is not None

    assert first.period is not None


def test_load_operations():

    loader = EvidenceLoader()

    evidence = loader.load_operations()

    assert len(evidence) > 0

    first = evidence[0]

    assert (
        first.source_type
        == "structured"
    )

    assert (
        first.source
        == "operations.csv"
    )

    assert (
        first.category
        == "inventory"
    )

    assert (
        first.metric
        == "inventory_availability"
    )

    assert first.value is not None


def test_load_business_context():

    loader = EvidenceLoader()

    evidence = (
        loader.load_business_context()
    )

    assert len(evidence) == 11

    first = evidence[0]

    assert (
        first.source_type
        == "unstructured"
    )

    assert (
        first.source
        == "business_context.json"
    )

    assert first.text is not None

    assert (
        first.region
        == "Region A"
    )

    assert (
        first.period
        == "2026-08"
    )


def test_business_context_contains_expected_sources():

    loader = EvidenceLoader()

    evidence = (
        loader.load_business_context()
    )

    categories = {
        item.category
        for item in evidence
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


def test_load_all():

    loader = EvidenceLoader()

    evidence = loader.load_all()

    assert len(evidence) > 0

    source_types = {
        item.source_type
        for item in evidence
    }

    assert (
        "structured"
        in source_types
    )

    assert (
        "unstructured"
        in source_types
    )