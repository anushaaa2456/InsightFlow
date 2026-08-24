from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Hypothesis:
    """
    Represents a possible explanation for an observed
    business change.

    A Hypothesis is NOT a confirmed causal conclusion.

    It is a candidate explanation that must be evaluated
    against evidence.
    """

    hypothesis_id: str

    statement: str

    driver: str

    evidence_ids: List[str] = field(
        default_factory=list
    )

    supporting_evidence_ids: List[str] = field(
        default_factory=list
    )

    contradicting_evidence_ids: List[str] = field(
        default_factory=list
    )

    confidence: Optional[str] = None

    confidence_score: Optional[float] = None

    status: str = "UNTESTED"

    reasoning: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self):
        """
        Validate the basic hypothesis contract.
        """

        if not self.hypothesis_id:
            raise ValueError(
                "hypothesis_id must not be empty."
            )

        if not self.statement:
            raise ValueError(
                "statement must not be empty."
            )

        if not self.driver:
            raise ValueError(
                "driver must not be empty."
            )

        valid_statuses = {
            "UNTESTED",
            "SUPPORTED",
            "PARTIALLY_SUPPORTED",
            "CONTRADICTED",
            "INSUFFICIENT_EVIDENCE",
        }

        if self.status not in valid_statuses:
            raise ValueError(
                "Invalid hypothesis status: "
                f"{self.status}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the hypothesis into a JSON-serializable
        dictionary.
        """

        return {
            "hypothesis_id": self.hypothesis_id,
            "statement": self.statement,
            "driver": self.driver,
            "evidence_ids": self.evidence_ids,
            "supporting_evidence_ids": (
                self.supporting_evidence_ids
            ),
            "contradicting_evidence_ids": (
                self.contradicting_evidence_ids
            ),
            "confidence": self.confidence,
            "confidence_score": (
                self.confidence_score
            ),
            "status": self.status,
            "reasoning": self.reasoning,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "Hypothesis":
        """
        Reconstruct a Hypothesis from a dictionary.
        """

        return cls(**data)