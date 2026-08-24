from pathlib import Path
import json

import pandas as pd

from src.evidence.models import Evidence


class EvidenceLoader:
    """
    Loads InsightFlow's structured and unstructured data
    and converts it into standardized Evidence objects.
    """

    def __init__(
        self,
        transactions_path=None,
        operations_path=None,
        context_path=None,
    ):
        project_root = Path(__file__).resolve().parents[2]

        self.transactions_path = Path(
            transactions_path
            or project_root
            / "data"
            / "raw"
            / "transactions.csv"
        )

        self.operations_path = Path(
            operations_path
            or project_root
            / "data"
            / "raw"
            / "operations.csv"
        )

        self.context_path = Path(
            context_path
            or project_root
            / "data"
            / "raw"
            / "business_context.json"
        )

    # ==========================================================
    # TRANSACTIONS
    # ==========================================================

    def load_transactions(self):
        """
        Load transaction-level structured evidence.

        Each transaction row becomes an Evidence object.

        The raw transaction fields are preserved in metadata so
        later stages can aggregate/filter them without losing
        provenance.
        """

        if not self.transactions_path.exists():
            raise FileNotFoundError(
                f"Transactions file not found: "
                f"{self.transactions_path}"
            )

        df = pd.read_csv(
            self.transactions_path
        )

        required_columns = {
            "date",
            "region",
            "channel",
            "customer_id",
            "product_id",
            "product_category",
            "customer_segment",
            "orders",
            "units",
            "revenue",
            "price",
            "discount",
        }

        missing = (
            required_columns
            - set(df.columns)
        )

        if missing:
            raise ValueError(
                "Transactions dataset is missing "
                f"required columns: {sorted(missing)}"
            )

        evidence = []

        for index, row in df.iterrows():

            date = pd.to_datetime(
                row["date"]
            )

            evidence.append(
                Evidence(
                    evidence_id=(
                        f"transaction_{index}"
                    ),
                    source_type="structured",
                    source="transactions.csv",
                    category="transaction",
                    metric="revenue",
                    value=float(
                        row["revenue"]
                    ),
                    direction="neutral",
                    period=date.strftime(
                        "%Y-%m"
                    ),
                    region=row["region"],
                    product_category=(
                        row["product_category"]
                    ),
                    product_id=row["product_id"],
                    channel=row["channel"],
                    customer_segment=(
                        row["customer_segment"]
                    ),
                    metadata={
                        "date": date.strftime(
                            "%Y-%m-%d"
                        ),
                        "customer_id": (
                            row["customer_id"]
                        ),
                        "orders": float(
                            row["orders"]
                        ),
                        "units": float(
                            row["units"]
                        ),
                        "price": float(
                            row["price"]
                        ),
                        "discount": float(
                            row["discount"]
                        ),
                    },
                )
            )

        return evidence

    # ==========================================================
    # OPERATIONS
    # ==========================================================

    def load_operations(self):
        """
        Load operational/inventory evidence.

        Each operations row becomes an Evidence object.

        Inventory availability is derived as:

            inventory_available
            --------------------
            inventory_capacity
        """

        if not self.operations_path.exists():
            raise FileNotFoundError(
                f"Operations file not found: "
                f"{self.operations_path}"
            )

        df = pd.read_csv(
            self.operations_path
        )

        required_columns = {
            "date",
            "region",
            "product_id",
            "inventory_available",
            "inventory_capacity",
            "stockout_hours",
        }

        missing = (
            required_columns
            - set(df.columns)
        )

        if missing:
            raise ValueError(
                "Operations dataset is missing "
                f"required columns: {sorted(missing)}"
            )

        evidence = []

        for index, row in df.iterrows():

            date = pd.to_datetime(
                row["date"]
            )

            capacity = float(
                row["inventory_capacity"]
            )

            available = float(
                row["inventory_available"]
            )

            if capacity > 0:
                availability = (
                    available / capacity
                )
            else:
                availability = None

            evidence.append(
                Evidence(
                    evidence_id=(
                        f"operation_{index}"
                    ),
                    source_type="structured",
                    source="operations.csv",
                    category="inventory",
                    metric=(
                        "inventory_availability"
                    ),
                    value=availability,
                    direction="neutral",
                    period=date.strftime(
                        "%Y-%m"
                    ),
                    region=row["region"],
                    product_id=row["product_id"],
                    metadata={
                        "date": date.strftime(
                            "%Y-%m-%d"
                        ),
                        "inventory_available": (
                            available
                        ),
                        "inventory_capacity": (
                            capacity
                        ),
                        "stockout_hours": float(
                            row["stockout_hours"]
                        ),
                    },
                )
            )

        return evidence

    # ==========================================================
    # BUSINESS CONTEXT
    # ==========================================================

    def load_business_context(self):
        """
        Load unstructured evidence from business_context.json.
        """

        if not self.context_path.exists():
            raise FileNotFoundError(
                f"Business context file not found: "
                f"{self.context_path}"
            )

        with open(
            self.context_path,
            "r",
            encoding="utf-8",
        ) as file:

            records = json.load(file)

        if not isinstance(records, list):
            raise ValueError(
                "business_context.json must contain "
                "a list of evidence records."
            )

        evidence = []

        for index, record in enumerate(records):

            date = record.get(
                "date"
            )

            period = None

            if date:
                period = pd.to_datetime(
                    date
                ).strftime(
                    "%Y-%m"
                )

            evidence.append(
                Evidence(
                    evidence_id=(
                        f"context_{index}"
                    ),
                    source_type="unstructured",
                    source="business_context.json",
                    category=(
                        record.get(
                            "source_type",
                            "business_context"
                        )
                    ),
                    text=record.get(
                        "text"
                    ),
                    period=period,
                    region=record.get(
                        "region"
                    ),
                    product_category=(
                        record.get(
                            "product_category"
                        )
                    ),
                    metadata={
                        "date": date,
                        "original_source_type": (
                            record.get(
                                "source_type"
                            )
                        ),
                        "original_source": (
                            record.get(
                                "source"
                            )
                        ),
                    },
                )
            )

        return evidence

    # ==========================================================
    # LOAD EVERYTHING
    # ==========================================================

    def load_all(self):
        """
        Load all available InsightFlow evidence sources.
        """

        evidence = []

        evidence.extend(
            self.load_transactions()
        )

        evidence.extend(
            self.load_operations()
        )

        evidence.extend(
            self.load_business_context()
        )

        return evidence