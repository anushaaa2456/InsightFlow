from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Evidence:
    """
    Represents one piece of evidence used during InsightFlow
    investigation.

    Evidence can come from structured datasets such as CSV files
    or unstructured sources such as customer reviews, sales notes,
    and competitor information.
    """

    evidence_id: str

    source_type: str

    source: str

    category: str

    text: Optional[str] = None

    metric: Optional[str] = None

    value: Optional[float] = None

    direction: Optional[str] = None

    period: Optional[str] = None

    region: Optional[str] = None

    product_category: Optional[str] = None

    product_id: Optional[str] = None

    channel: Optional[str] = None

    customer_segment: Optional[str] = None

    relevance: Optional[float] = None

    reliability: Optional[float] = None

    relevance_reasons: list[str] = field(
    default_factory=list
)

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self):
        """
        Validate the basic Evidence contract.
        """

        if not self.evidence_id:
            raise ValueError(
                "evidence_id must not be empty."
            )

        if self.source_type not in {
            "structured",
            "unstructured",
        }:
            raise ValueError(
                "source_type must be either "
                "'structured' or 'unstructured'."
            )

        if not self.source:
            raise ValueError(
                "source must not be empty."
            )

        if not self.category:
            raise ValueError(
                "category must not be empty."
            )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Evidence object into a JSON-serializable
        dictionary.
        """

        return {
            "evidence_id": self.evidence_id,
            "source_type": self.source_type,
            "source": self.source,
            "category": self.category,
            "text": self.text,
            "metric": self.metric,
            "value": self.value,
            "direction": self.direction,
            "period": self.period,
            "region": self.region,
            "product_category": self.product_category,
            "product_id": self.product_id,
            "channel": self.channel,
            "customer_segment": self.customer_segment,
            "relevance": self.relevance,
            "reliability": self.reliability,
            "relevance_reasons": self.relevance_reasons,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "Evidence":
        """
        Reconstruct an Evidence object from a dictionary.
        """

        return cls(**data)