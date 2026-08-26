import json

import pytest

from src.evidence.models import Evidence


def test_structured_evidence():

    evidence = Evidence(
        evidence_id="inventory_region_a_august",
        source_type="structured",
        source="operations.csv",
        category="inventory",
        metric="inventory_availability",
        value=0.932,
        direction="decrease",
        period="2026-08",
        region="Region A",
    )

    assert (
        evidence.source_type
        == "structured"
    )

    assert (
        evidence.source
        == "operations.csv"
    )

    assert (
        evidence.category
        == "inventory"
    )

    assert (
        evidence.metric
        == "inventory_availability"
    )

    assert evidence.value == pytest.approx(
        0.932
    )

    assert (
        evidence.region
        == "Region A"
    )

    assert (
        evidence.period
        == "2026-08"
    )


def test_unstructured_evidence():

    evidence = Evidence(
        evidence_id="review_001",
        source_type="unstructured",
        source="business_context.json",
        category="customer_review",
        text=(
            "Customers reported difficulty "
            "finding premium products in stock."
        ),
        period="2026-08",
        region="Region A",
        product_category="Premium",
    )

    assert (
        evidence.source_type
        == "unstructured"
    )

    assert (
        evidence.source
        == "business_context.json"
    )

    assert (
        evidence.category
        == "customer_review"
    )

    assert (
        "difficulty finding premium"
        in evidence.text
    )

    assert (
        evidence.region
        == "Region A"
    )

    assert (
        evidence.period
        == "2026-08"
    )


def test_evidence_to_dict_is_json_serializable():

    evidence = Evidence(
        evidence_id="review_001",
        source_type="unstructured",
        source="business_context.json",
        category="customer_review",
        text="Premium products were difficult to find.",
        period="2026-08",
        region="Region A",
    )

    result = evidence.to_dict()

    json_string = json.dumps(result)

    assert isinstance(
        json_string,
        str
    )

    assert (
        result["evidence_id"]
        == "review_001"
    )


def test_invalid_source_type():

    with pytest.raises(ValueError):

        Evidence(
            evidence_id="bad_001",
            source_type="fake",
            source="something.csv",
            category="inventory",
        )


def test_empty_evidence_id():

    with pytest.raises(ValueError):

        Evidence(
            evidence_id="",
            source_type="structured",
            source="operations.csv",
            category="inventory",
        )


def test_optional_fields_can_be_none():

    evidence = Evidence(
        evidence_id="review_002",
        source_type="unstructured",
        source="business_context.json",
        category="customer_review",
    )

    assert evidence.text is None

    assert evidence.metric is None

    assert evidence.value is None

    assert evidence.region is None