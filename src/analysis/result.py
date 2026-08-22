from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DriverResult:
    """
    Standardized representation of a quantified KPI driver.
    """

    name: str
    label: str

    previous_value: Optional[float] = None
    current_value: Optional[float] = None

    change_pct: Optional[float] = None

    contribution_pp: Optional[float] = None

    rank: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create a DriverResult from the internal
        contribution-engine representation.
        """

        return cls(
            name=data["name"],
            label=data["label"],
            previous_value=data.get(
                "previous_value"
            ),
            current_value=data.get(
                "current_value"
            ),
            change_pct=data.get(
                "change_pct"
            ),
            contribution_pp=data.get(
                "contribution_pp"
            ),
            rank=data.get(
                "rank"
            ),
        )

    def to_dict(self):
        """
        Convert to a JSON-serializable dictionary.
        """

        return {
            "name": self.name,
            "label": self.label,
            "previous_value": self.previous_value,
            "current_value": self.current_value,
            "change_pct": self.change_pct,
            "contribution_pp": self.contribution_pp,
            "rank": self.rank,
        }


@dataclass
class AnalysisResult:
    """
    Stable downstream contract produced by InsightFlow's
    analytical engine.

    This object is the handoff between:

        Person 1:
        WHAT changed / WHERE / HOW MUCH

    and:

        Person 2:
        WHY did it happen?

    The result deliberately contains analytical facts,
    not hypotheses or causal claims.
    """

    kpi: str

    entity_dimension: str

    entity: str

    previous_period: str

    current_period: str

    previous_value: Optional[float]

    current_value: Optional[float]

    absolute_change: Optional[float]

    change_pct: Optional[float]

    direction: str

    is_material: bool

    decision: str

    drivers: List[DriverResult] = field(
        default_factory=list
    )

    primary_driver: Optional[DriverResult] = None

    drill_down: List[Dict[str, Any]] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # ==========================================================
    # CONVERSION
    # ==========================================================

    def to_dict(self):
        """
        Convert the analysis result into a plain
        JSON-serializable dictionary.
        """

        return {
            "kpi": self.kpi,

            "entity": {
                "dimension": self.entity_dimension,
                "value": self.entity,
            },

            "period": {
                "previous": self.previous_period,
                "current": self.current_period,
            },

            "change": {
                "previous_value": self.previous_value,
                "current_value": self.current_value,
                "absolute_change": self.absolute_change,
                "change_pct": self.change_pct,
                "direction": self.direction,
            },

            "materiality": {
                "is_material": self.is_material,
                "decision": self.decision,
            },

            "drivers": [
                driver.to_dict()
                for driver in self.drivers
            ],

            "primary_driver": (
                self.primary_driver.to_dict()
                if self.primary_driver
                else None
            ),

            "drill_down": self.drill_down,

            "metadata": self.metadata,
        }

    # ==========================================================
    # FACT-ONLY PAYLOAD
    # ==========================================================

    def to_evidence_payload(self):
        """
        Return only the analytical facts that should be
        handed to the evidence / hypothesis layer.

        Deliberately excludes causal interpretations.
        """

        return {
            "kpi": self.kpi,

            "entity": {
                "dimension": self.entity_dimension,
                "value": self.entity,
            },

            "period": {
                "previous": self.previous_period,
                "current": self.current_period,
            },

            "change": {
                "previous_value": self.previous_value,
                "current_value": self.current_value,
                "absolute_change": self.absolute_change,
                "change_pct": self.change_pct,
                "direction": self.direction,
            },

            "materiality": {
                "is_material": self.is_material,
                "decision": self.decision,
            },

            "drivers": [
                driver.to_dict()
                for driver in self.drivers
            ],

            "primary_driver": (
                self.primary_driver.to_dict()
                if self.primary_driver
                else None
            ),

            "drill_down": self.drill_down,
        }