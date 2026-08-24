from typing import Any, List

from src.evidence.loader import EvidenceLoader
from src.evidence.retriever import EvidenceRetriever
from src.hypothesis.evaluator import HypothesisEvaluator
from src.hypothesis.generator import HypothesisGenerator
from src.investigation.result import InvestigationResult


class InvestigationPipeline:
    """
    Orchestrates the complete Person 2 investigation flow.

        AnalysisResult
            ↓
        Evidence retrieval
            ↓
        Hypothesis generation
            ↓
        Hypothesis evaluation
            ↓
        InvestigationResult
    """

    def __init__(
        self,
        evidence=None,
        evidence_loader=None,
        evidence_retriever=None,
        hypothesis_generator=None,
        hypothesis_evaluator=None,
    ):
        """
        Dependencies can be injected for testing.

        If evidence is not supplied, the pipeline loads the
        real project evidence from the raw data files.
        """

        self.evidence_loader = (
            evidence_loader
            or EvidenceLoader()
        )

        if evidence is None:
            evidence = (
                self.evidence_loader.load_all()
            )

        self.evidence = list(
            evidence
        )

        self.evidence_retriever = (
            evidence_retriever
            or EvidenceRetriever(
                self.evidence
            )
        )

        self.hypothesis_generator = (
            hypothesis_generator
            or HypothesisGenerator()
        )

        self.hypothesis_evaluator = (
            hypothesis_evaluator
            or HypothesisEvaluator()
        )

    # ==========================================================
    # INVESTIGATE
    # ==========================================================

    def investigate(
        self,
        analysis_result: Any,
    ) -> InvestigationResult:
        """
        Run the complete Person 2 investigation.

        Parameters
        ----------
        analysis_result:
            Person 1 AnalysisResult or its evidence payload.

        Returns
        -------
        InvestigationResult
        """

        payload = (
            self._normalize_payload(
                analysis_result
            )
        )

        # ------------------------------------------------------
        # 1. Retrieve relevant evidence
        # ------------------------------------------------------

        evidence = (
            self.evidence_retriever.retrieve(
                payload,
                max_results=50,
            )
        )

        # ------------------------------------------------------
        # 2. Generate candidate hypotheses
        # ------------------------------------------------------

        hypotheses = (
            self.hypothesis_generator.generate(
                payload,
                evidence,
            )
        )

        # ------------------------------------------------------
        # 3. Evaluate each hypothesis
        # ------------------------------------------------------

        evaluated_hypotheses = []

        for hypothesis in hypotheses:

            evaluated = (
                self.hypothesis_evaluator.evaluate(
                    hypothesis,
                    evidence,
                )
            )

            evaluated_hypotheses.append(
                evaluated
            )

        # ------------------------------------------------------
        # 4. Select primary hypothesis
        # ------------------------------------------------------

        primary_hypothesis = (
            self._select_primary_hypothesis(
                evaluated_hypotheses
            )
        )

        # ------------------------------------------------------
        # 5. Build final investigation result
        # ------------------------------------------------------

        return InvestigationResult(
            kpi=payload["kpi"],
            entity_dimension=(
                payload["entity"]["dimension"]
            ),
            entity=(
                payload["entity"]["value"]
            ),
            previous_period=(
                payload["period"]["previous"]
            ),
            current_period=(
                payload["period"]["current"]
            ),
            primary_driver=(
                payload.get(
                    "primary_driver",
                    {}
                ).get("name")
                if isinstance(
                    payload.get(
                        "primary_driver"
                    ),
                    dict,
                )
                else None
            ),
            evidence=evidence,
            hypotheses=evaluated_hypotheses,
            primary_hypothesis=(
                primary_hypothesis
            ),
            metadata={
                "evidence_count": len(
                    evidence
                ),
                "hypothesis_count": len(
                    evaluated_hypotheses
                ),
            },
        )

    # ==========================================================
    # NORMALIZATION
    # ==========================================================

    @staticmethod
    def _normalize_payload(
        analysis_result: Any,
    ):

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
            "AnalysisResult or evidence payload dictionary."
        )

    # ==========================================================
    # PRIMARY HYPOTHESIS
    # ==========================================================

    @staticmethod
    def _select_primary_hypothesis(
        hypotheses: List[Any],
    ):
        """
        Select the strongest evaluated hypothesis.

        Ranking:

            1. confidence score
            2. supporting evidence count
            3. fewer contradictions

        A hypothesis with no evidence is never selected.
        """

        if not hypotheses:
            return None

        candidates = [
            hypothesis
            for hypothesis in hypotheses
            if (
                len(
                    hypothesis
                    .supporting_evidence_ids
                )
                > 0
            )
        ]

        if not candidates:
            return None

        candidates.sort(
            key=lambda hypothesis: (
                hypothesis.confidence_score
                if hypothesis.confidence_score
                is not None
                else 0.0,

                len(
                    hypothesis
                    .supporting_evidence_ids
                ),

                -len(
                    hypothesis
                    .contradicting_evidence_ids
                ),
            ),
            reverse=True,
        )

        return candidates[0]