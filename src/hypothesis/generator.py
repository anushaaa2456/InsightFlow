from typing import Any, Dict, List

from src.hypothesis.models import Hypothesis


class HypothesisGenerator:
    """
    Generates candidate explanations from Person 1's analytical
    result and the evidence retrieved by Person 2.

    This class proposes hypotheses.

    It does NOT:
        - prove causality
        - calculate confidence
        - select the final root cause
    """

    # ==========================================================
    # HYPOTHESIS TEMPLATES
    # ==========================================================

    DRIVER_HYPOTHESES = {
        "aov": [
            {
                "id": "price_pressure",
                "statement": (
                    "Price changes contributed to the "
                    "AOV change."
                ),
                "categories": {
                    "price",
                    "competitor_news",
                    "sales_note",
                },
            },
            {
                "id": "discounting",
                "statement": (
                    "Changes in discounting contributed "
                    "to the AOV change."
                ),
                "categories": {
                    "discount",
                    "sales_note",
                },
            },
            {
                "id": "premium_mix",
                "statement": (
                    "A change in premium product mix "
                    "contributed to the AOV change."
                ),
                "categories": {
                    "premium_mix",
                    "product_mix",
                    "inventory",
                    "customer_review",
                    "sales_note",
                },
            },
            {
                "id": "inventory_constraints",
                "statement": (
                    "Inventory constraints contributed "
                    "to the AOV change."
                ),
                "categories": {
                    "inventory",
                    "stockout",
                    "customer_review",
                    "sales_note",
                },
            },
        ],
        "active_customers": [
            {
                "id": "customer_behavior",
                "statement": (
                    "Changes in customer behavior contributed "
                    "to the active-customer change."
                ),
                "categories": {
                    "customer_behavior",
                    "customer_review",
                    "sales_note",
                },
            },
        ],
        "orders_per_customer": [
            {
                "id": "purchase_frequency",
                "statement": (
                    "Changes in purchase behavior contributed "
                    "to the orders-per-customer change."
                ),
                "categories": {
                    "customer_behavior",
                    "customer_review",
                    "sales_note",
                },
            },
        ],
    }

    def generate(
        self,
        analysis_result: Any,
        evidence: List[Any],
    ) -> List[Hypothesis]:
        """
        Generate candidate hypotheses based on the primary
        driver and available evidence.

        Evidence is used to determine which candidate
        explanations are relevant.

        It is NOT used here to determine whether a hypothesis
        is true.
        """

        payload = self._normalize_payload(
            analysis_result
        )

        primary_driver = self._get_primary_driver(
            payload
        )

        if not primary_driver:
            return []

        templates = self.DRIVER_HYPOTHESES.get(
            primary_driver,
            [],
        )

        hypotheses = []

        for template in templates:
            relevant_evidence = [
                item
                for item in evidence
                if (
                    item.category in template["categories"]
                    and (
                        item.relevance is None
                        or item.relevance >= 0.70
                    )
                )
            ]

            relevant_evidence = sorted(
                relevant_evidence,
                key=lambda item: (
                    item.relevance
                    if item.relevance is not None
                    else 0.0
                ),
                reverse=True,
            )[:10]

            # Only generate a hypothesis when there is
            # at least some evidence category relevant
            # to that hypothesis.
            if not relevant_evidence:
                continue

            evidence_ids = [
                item.evidence_id
                for item in relevant_evidence
            ]

            hypotheses.append(
                Hypothesis(
                    hypothesis_id=(
                        f"{primary_driver}_"
                        f"{template['id']}"
                    ),
                    statement=(
                        template["statement"]
                    ),
                    driver=primary_driver,
                    evidence_ids=evidence_ids,
                    status="UNTESTED",
                    metadata={
                        "candidate_category": (
                            template["id"]
                        ),
                        "evidence_count": len(
                            relevant_evidence
                        ),
                    },
                )
            )

        return hypotheses

    # ==========================================================
    # NORMALIZATION
    # ==========================================================

    @staticmethod
    def _normalize_payload(
        analysis_result: Any,
    ) -> Dict[str, Any]:

        if hasattr(
            analysis_result,
            "to_evidence_payload",
        ):
            return (
                analysis_result
                .to_evidence_payload()
            )

        if isinstance(
            analysis_result,
            dict,
        ):
            return analysis_result

        raise TypeError(
            "analysis_result must be an "
            "AnalysisResult or dictionary."
        )

    # ==========================================================
    # PRIMARY DRIVER
    # ==========================================================

    @staticmethod
    def _get_primary_driver(
        payload: Dict[str, Any],
    ) -> str | None:

        primary_driver = payload.get(
            "primary_driver"
        )

        if not isinstance(
            primary_driver,
            dict,
        ):
            return None

        return primary_driver.get(
            "name"
        )