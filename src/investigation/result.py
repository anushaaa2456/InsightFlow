from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.evidence.models import Evidence
from src.hypothesis.models import Hypothesis


@dataclass
class InvestigationResult:
    """
    Structured output of Person 2's investigation.

    This object combines:

        Person 1 analytical facts
        +
        retrieved evidence
        +
        evaluated hypotheses

    It does NOT claim absolute causal certainty.
    """

    kpi: str

    entity_dimension: str

    entity: str

    previous_period: str

    current_period: str

    primary_driver: Optional[str] = None

    evidence: List[Evidence] = field(
        default_factory=list
    )

    hypotheses: List[Hypothesis] = field(
        default_factory=list
    )

    primary_hypothesis: Optional[
        Hypothesis
    ] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the investigation result into a
        JSON-serializable dictionary.
        """

        return {
            "kpi": self.kpi,

            "entity": {
                "dimension": (
                    self.entity_dimension
                ),
                "value": self.entity,
            },

            "period": {
                "previous": (
                    self.previous_period
                ),
                "current": (
                    self.current_period
                ),
            },

            "primary_driver": (
                self.primary_driver
            ),

            "evidence": [
                item.to_dict()
                for item in self.evidence
            ],

            "hypotheses": [
                hypothesis.to_dict()
                for hypothesis in self.hypotheses
            ],

            "primary_hypothesis": (
                self.primary_hypothesis.to_dict()
                if self.primary_hypothesis
                else None
            ),

            "metadata": self.metadata,
        }