from typing import Any, Dict, List

from src.evidence.models import Evidence


class EvidenceRetriever:
    """
    Retrieves evidence relevant to a Person 1 AnalysisResult
    or evidence payload.

    The retriever is intentionally deterministic.

    It does not:
        - generate hypotheses
        - determine causality
        - calculate confidence

    Its only responsibility is:

        analytical facts
            ↓
        relevant evidence
    """

    # ==========================================================
    # DRIVER → EVIDENCE CATEGORIES
    # ==========================================================

    DRIVER_CATEGORIES = {
        "aov": {
            "price",
            "discount",
            "product_mix",
            "premium_mix",
            "inventory",
            "stockout",
            "customer_review",
            "competitor_news",
            "sales_note",
        },

        "active_customers": {
            "customer_behavior",
            "customer_review",
            "sales_note",
        },

        "orders_per_customer": {
            "customer_behavior",
            "customer_review",
            "sales_note",
        },
    }

    # ==========================================================
    # RELEVANCE LABEL
    # ==========================================================

    @staticmethod
    def relevance_label(
        relevance: float,
    ) -> str:
        """
        Convert numeric relevance into an explainable label.
        """

        if relevance >= 0.90:
            return "HIGH"

        if relevance >= 0.70:
            return "MEDIUM"

        return "LOW"

    # ==========================================================
    # CONSTRUCTOR
    # ==========================================================

    def __init__(
        self,
        evidence: List[Evidence],
    ):
        self.evidence = list(
            evidence
        )

    # ==========================================================
    # PAYLOAD NORMALIZATION
    # ==========================================================

    @staticmethod
    def _normalize_payload(
        analysis_result: Any,
    ) -> Dict[str, Any]:
        """
        Accept either:

            AnalysisResult

        or:

            AnalysisResult.to_evidence_payload()

        This keeps the retriever flexible while still using
        the stable Person 1 contract.
        """

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
            "AnalysisResult or an evidence payload dictionary."
        )

    # ==========================================================
    # EXTRACT ENTITY
    # ==========================================================

    @staticmethod
    def _get_entity(
        payload: Dict[str, Any],
    ) -> str | None:

        entity = payload.get(
            "entity"
        )

        if not isinstance(
            entity,
            dict,
        ):
            return None

        return entity.get(
            "value"
        )

    # ==========================================================
    # EXTRACT CURRENT PERIOD
    # ==========================================================

    @staticmethod
    def _get_current_period(
        payload: Dict[str, Any],
    ) -> str | None:

        period = payload.get(
            "period"
        )

        if not isinstance(
            period,
            dict,
        ):
            return None

        return period.get(
            "current"
        )

    # ==========================================================
    # EXTRACT PREVIOUS PERIOD
    # ==========================================================

    @staticmethod
    def _get_previous_period(
        payload: Dict[str, Any],
    ) -> str | None:

        period = payload.get(
            "period"
        )

        if not isinstance(
            period,
            dict,
        ):
            return None

        return period.get(
            "previous"
        )

    # ==========================================================
    # EXTRACT PRIMARY DRIVER
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

    # ==========================================================
    # RELEVANT CATEGORIES
    # ==========================================================

    def _get_relevant_categories(
        self,
        primary_driver: str | None,
    ) -> set[str]:

        if not primary_driver:
            return set()

        return self.DRIVER_CATEGORIES.get(
            primary_driver,
            set(),
        )

    # ==========================================================
    # RELEVANCE SCORE
    # ==========================================================

    def _calculate_relevance(
        self,
        item: Evidence,
        entity: str | None,
        current_period: str | None,
        previous_period: str | None,
        relevant_categories: set[str],
    ):
        """
        Calculate deterministic evidence relevance.

        Scoring:

            same region       +0.40
            current period    +0.30
            relevant category +0.30

        Previous-period evidence is retained for
        period-over-period comparison but does not receive
        the current-period bonus.

        Maximum score = 1.00.

        Returns both the numeric score and the reasons
        contributing to that score.
        """

        score = 0.0

        reasons = []

        # --------------------------------------------------
        # Region
        # --------------------------------------------------

        if (
            entity is not None
            and item.region == entity
        ):
            score += 0.40

            reasons.append(
                "same_region"
            )

        # --------------------------------------------------
        # Period
        # --------------------------------------------------

        if (
            current_period is not None
            and item.period == current_period
        ):
            score += 0.30

            reasons.append(
                "same_period"
            )

        elif (
            previous_period is not None
            and item.period == previous_period
        ):
            reasons.append(
                "previous_period"
            )

        # --------------------------------------------------
        # Driver/category relevance
        # --------------------------------------------------

        if (
            item.category
            in relevant_categories
        ):
            score += 0.30

            reasons.append(
                "relevant_to_primary_driver"
            )

        return (
            round(
                score,
                4,
            ),
            reasons,
        )

    # ==========================================================
    # RETRIEVE
    # ==========================================================

    def retrieve(
        self,
        analysis_result: Any,
        minimum_relevance: float = 0.60,
        max_results: int | None = None,
    ) -> List[Evidence]:
        """
        Retrieve evidence relevant to the analytical result.

        Evidence is scoped to:

            1. the requested entity/region
            2. the current reporting period
            3. the previous reporting period
            4. categories relevant to the primary driver

        Evidence from unrelated entities or periods is excluded.

        Evidence is returned in descending relevance order.

        Parameters
        ----------
        analysis_result:
            AnalysisResult or evidence payload dictionary.

        minimum_relevance:
            Minimum relevance score required for evidence
            to be returned.

        max_results:
            Optional maximum number of evidence records to return.

            If None, all qualifying evidence is returned.
        """

        payload = (
            self._normalize_payload(
                analysis_result
            )
        )

        # --------------------------------------------------
        # Extract investigation scope
        # --------------------------------------------------

        entity = self._get_entity(
            payload
        )

        current_period = (
            self._get_current_period(
                payload
            )
        )

        previous_period = (
            self._get_previous_period(
                payload
            )
        )

        primary_driver = (
            self._get_primary_driver(
                payload
            )
        )

        relevant_categories = (
            self._get_relevant_categories(
                primary_driver
            )
        )

        ranked = []

        for item in self.evidence:

            # --------------------------------------------------
            # ENTITY SCOPE
            # --------------------------------------------------
            #
            # If the investigation specifies an entity/region,
            # do not use evidence explicitly belonging to a
            # different entity.
            #
            if (
                entity is not None
                and item.region is not None
                and item.region != entity
            ):
                continue

            # --------------------------------------------------
            # PERIOD SCOPE
            # --------------------------------------------------
            #
            # Only current or previous reporting periods are
            # relevant to a period-over-period investigation.
            #
            if (
                item.period is not None
                and item.period not in {
                    current_period,
                    previous_period,
                }
            ):
                continue

            # --------------------------------------------------
            # RELEVANCE
            # --------------------------------------------------

            relevance, reasons = (
                self._calculate_relevance(
                    item=item,
                    entity=entity,
                    current_period=current_period,
                    previous_period=previous_period,
                    relevant_categories=(
                        relevant_categories
                    ),
                )
            )

            # --------------------------------------------------
            # MINIMUM RELEVANCE
            # --------------------------------------------------

            if (
                relevance
                >= minimum_relevance
            ):

                item.relevance = relevance

                item.relevance_reasons = (
                    reasons
                )

                ranked.append(
                    (
                        relevance,
                        item,
                    )
                )

        # --------------------------------------------------
        # SORT
        # --------------------------------------------------

        ranked.sort(
            key=lambda pair: pair[0],
            reverse=True,
        )

        # --------------------------------------------------
        # LIMIT RESULTS
        # --------------------------------------------------

        if max_results is not None:

            if max_results < 0:
                raise ValueError(
                    "max_results must be "
                    "non-negative or None."
                )

            ranked = ranked[
                :max_results
            ]

        # --------------------------------------------------
        # BUILD RESULTS
        # --------------------------------------------------

        results = []

        for relevance, item in ranked:

            item.relevance = relevance

            results.append(
                item
            )

        return results

    # ==========================================================
    # GROUP BY CATEGORY
    # ==========================================================

    def retrieve_by_category(
        self,
        analysis_result: Any,
        minimum_relevance: float = 0.60,
        max_results: int | None = None,
    ) -> Dict[
        str,
        List[Evidence],
    ]:
        """
        Retrieve relevant evidence and group it by category.

        max_results, when supplied, limits the total number of
        retrieved evidence records before grouping.
        """

        evidence = self.retrieve(
            analysis_result=analysis_result,
            minimum_relevance=(
                minimum_relevance
            ),
            max_results=max_results,
        )

        grouped = {}

        for item in evidence:

            grouped.setdefault(
                item.category,
                [],
            ).append(
                item
            )

        return grouped