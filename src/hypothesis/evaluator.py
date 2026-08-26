from typing import Any, List

from src.hypothesis.models import Hypothesis


class HypothesisEvaluator:
    """
    Evaluates candidate hypotheses against retrieved evidence.

    This component determines the evidentiary status of a
    hypothesis.

    It does NOT claim scientific or causal certainty.
    """

    MIN_SUPPORTING_EVIDENCE = 1

    # ==========================================================
    # HYPOTHESIS → EVIDENCE CATEGORIES
    # ==========================================================

    CATEGORY_MAPPING = {
        "price_pressure": {
            "price",
            "competitor_news",
        },

        "discounting": {
            "discount",
        },

        "premium_mix": {
            "premium_mix",
            "product_mix",
        },

        "inventory_constraints": {
            "inventory",
            "stockout",
        },
    }

    # ==========================================================
    # EVALUATE
    # ==========================================================

    def evaluate(
        self,
        hypothesis: Hypothesis,
        evidence: List[Any],
    ) -> Hypothesis:
        """
        Evaluate one hypothesis against evidence.
        """

        evidence_by_id = {
            item.evidence_id: item
            for item in evidence
        }

        supporting = []
        contradicting = []

        for evidence_id in hypothesis.evidence_ids:

            item = evidence_by_id.get(
                evidence_id
            )

            if item is None:
                continue

            # --------------------------------------------------
            # Contradiction must be checked first.
            # --------------------------------------------------

            if self._contradicts(
                hypothesis,
                item,
            ):
                contradicting.append(
                    evidence_id
                )

            elif self._supports(
                hypothesis,
                item,
            ):
                supporting.append(
                    evidence_id
                )

        hypothesis.supporting_evidence_ids = (
            supporting
        )

        hypothesis.contradicting_evidence_ids = (
            contradicting
        )

        status = self._determine_status(
            supporting_count=len(
                supporting
            ),
            contradicting_count=len(
                contradicting
            ),
        )

        hypothesis.status = status

        hypothesis.confidence_score = (
            self._calculate_score(
                supporting_count=len(
                    supporting
                ),
                contradicting_count=len(
                    contradicting
                ),
            )
        )

        hypothesis.confidence = (
            self._confidence_label(
                score=hypothesis.confidence_score,
                supporting_count=len(
                    supporting
                ),
                contradicting_count=len(
                    contradicting
                ),
            )
        )

        hypothesis.reasoning = (
            self._build_reasoning(
                supporting_count=len(
                    supporting
                ),
                contradicting_count=len(
                    contradicting
                ),
                status=status,
            )
        )

        return hypothesis

    # ==========================================================
    # SUPPORT
    # ==========================================================

    @classmethod
    def _supports(
        cls,
        hypothesis: Hypothesis,
        evidence: Any,
    ) -> bool:
        """
        Determine whether evidence supports a hypothesis.

        The evaluator uses the candidate category to determine
        whether an evidence category is relevant.

        Generic customer reviews and sales notes are NOT treated
        as automatic causal support.
        """

        candidate_category = (
            hypothesis.metadata.get(
                "candidate_category"
            )
        )

        if candidate_category is None:
            return False

        category = getattr(
            evidence,
            "category",
            None,
        )

        if category is None:
            return False

        allowed_categories = (
            cls.CATEGORY_MAPPING.get(
                candidate_category,
                set(),
            )
        )

        # ------------------------------------------------------
        # Direct category match
        # ------------------------------------------------------

        if category in allowed_categories:

            # Inventory/stockout evidence directly supports
            # inventory constraints.
            if candidate_category == (
                "inventory_constraints"
            ):
                return True

            # Premium mix requires actual premium/product-mix
            # evidence. Generic inventory records do not qualify.
            if candidate_category == (
                "premium_mix"
            ):
                return category in {
                    "premium_mix",
                    "product_mix",
                }

            # Price pressure requires explicit price-related
            # evidence.
            if candidate_category == (
                "price_pressure"
            ):
                if category == "price":
                    return True

                if category == "competitor_news":
                    return cls._contains_price_signal(
                        evidence
                    )

                return False

            # Discounting requires explicit discount evidence.
            if candidate_category == (
                "discounting"
            ):
                return category == "discount"

            return True

        return False

    # ==========================================================
    # PRICE SIGNAL
    # ==========================================================

    @staticmethod
    def _contains_price_signal(
        evidence: Any,
    ) -> bool:
        """
        Determine whether competitor/news evidence contains
        an explicit pricing signal.
        """

        text = getattr(
            evidence,
            "text",
            None,
        )

        if not isinstance(
            text,
            str,
        ):
            return False

        text_lower = text.lower()

        price_terms = {
            "price",
            "pricing",
            "priced",
            "discount",
            "reduced",
            "cheaper",
            "cost",
        }

        return any(
            term in text_lower
            for term in price_terms
        )

    # ==========================================================
    # CONTRADICTION
    # ==========================================================

    @staticmethod
    def _contradicts(
        hypothesis: Hypothesis,
        evidence: Any,
    ) -> bool:
        """
        Determine whether evidence explicitly contradicts
        a hypothesis.
        """

        metadata = getattr(
            evidence,
            "metadata",
            {},
        )

        if not isinstance(
            metadata,
            dict,
        ):
            return False

        return bool(
            metadata.get(
                "contradicts_hypothesis",
                False,
            )
        )

    # ==========================================================
    # STATUS
    # ==========================================================

    @staticmethod
    def _determine_status(
        supporting_count: int,
        contradicting_count: int,
    ) -> str:
        """
        Determine the evidentiary status.
        """

        if (
            supporting_count == 0
            and contradicting_count == 0
        ):
            return "INSUFFICIENT_EVIDENCE"

        if (
            contradicting_count
            > supporting_count
        ):
            return "CONTRADICTED"

        if (
            supporting_count >= 2
            and contradicting_count == 0
        ):
            return "SUPPORTED"

        if (
            supporting_count >= 1
            and contradicting_count == 0
        ):
            return "PARTIALLY_SUPPORTED"

        return "PARTIALLY_SUPPORTED"

    # ==========================================================
    # SCORE
    # ==========================================================

    @staticmethod
    def _calculate_score(
        supporting_count: int,
        contradicting_count: int,
    ) -> float:
        """
        Calculate the support ratio.
        """

        total = (
            supporting_count
            + contradicting_count
        )

        if total == 0:
            return 0.0

        score = (
            supporting_count / total
        )

        return round(
            score,
            4,
        )

    # ==========================================================
    # CONFIDENCE
    # ==========================================================

    @staticmethod
    def _confidence_label(
        score: float,
        supporting_count: int,
        contradicting_count: int,
    ) -> str:
        """
        Convert evidentiary support into a confidence label.
        """

        # One supporting item is LOW confidence.
        if (
            supporting_count == 1
            and contradicting_count == 0
        ):
            return "LOW"

        # Multiple clean supporting items.
        if (
            supporting_count >= 2
            and contradicting_count == 0
            and score >= 0.80
        ):
            return "HIGH"

        # Mixed evidence.
        if (
            supporting_count >= 2
            and score >= 0.50
        ):
            return "MEDIUM"

        return "LOW"

    # ==========================================================
    # REASONING
    # ==========================================================

    @staticmethod
    def _build_reasoning(
        supporting_count: int,
        contradicting_count: int,
        status: str,
    ) -> str:

        return (
            f"Evidence evaluation found "
            f"{supporting_count} supporting "
            f"and "
            f"{contradicting_count} contradicting "
            f"items. "
            f"Result: {status}."
        )