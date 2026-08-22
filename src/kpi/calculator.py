from pathlib import Path

import pandas as pd

from src.kpi.registry import KPIRegistry


class KPICalculator:
    """
    Calculates KPIs using definitions stored in the KPI semantic registry.
    """

    def __init__(self, registry=None):
        self.registry = registry or KPIRegistry()

    def load_data(self, kpi_name):
        """
        Load the dataset associated with the KPI.
        """

        kpi_config = self.registry.get(kpi_name)

        relative_path = kpi_config["data_source"]["file"]

        project_root = Path(__file__).resolve().parents[2]
        data_path = project_root / relative_path

        if not data_path.exists():
            raise FileNotFoundError(
                f"Data file not found: {data_path}"
            )

        return pd.read_csv(data_path)

    def calculate(
        self,
        kpi_name,
        group_by=None,
        filters=None
    ):
        """
        Calculate a KPI using the configuration in the KPI registry.

        Parameters
        ----------
        kpi_name : str
            Name of the KPI registered in kpi_registry.yaml.

        group_by : list[str], optional
            Dimensions by which to aggregate the KPI.

            Examples:
                ["region"]
                ["region", "month"]
                ["region", "product"]

        filters : dict, optional
            Column-value filters.

            Examples:
                {"region": "Region A"}

                {"region": ["Region A", "Region B"]}

        Returns
        -------
        pandas.DataFrame
            Aggregated KPI values.
        """

        # --------------------------------------------------
        # Load KPI configuration
        # --------------------------------------------------

        kpi_config = self.registry.get(kpi_name)
        calculation = kpi_config["calculation"]

        # --------------------------------------------------
        # Load source data
        # --------------------------------------------------

        df = self.load_data(kpi_name)

        # --------------------------------------------------
        # Standardize date fields
        # --------------------------------------------------

        group_by = group_by or []

        if "date" in df.columns:
            df["date"] = pd.to_datetime(
                df["date"],
                errors="coerce"
            )

        # Create monthly reporting dimension when requested
        if "month" in group_by:

            if "date" not in df.columns:
                raise ValueError(
                    "Cannot create 'month' dimension because "
                    "the dataset does not contain a 'date' column."
                )

            df["month"] = (
                df["date"]
                .dt.to_period("M")
                .astype(str)
            )

        # --------------------------------------------------
        # Apply filters
        # --------------------------------------------------

        if filters:

            for column, value in filters.items():

                if column not in df.columns:
                    raise ValueError(
                        f"Filter column '{column}' "
                        f"not found in dataset."
                    )

                if isinstance(value, list):
                    df = df[df[column].isin(value)]

                else:
                    df = df[df[column] == value]

        # --------------------------------------------------
        # Validate grouping columns
        # --------------------------------------------------

        for column in group_by:

            if column not in df.columns:
                raise ValueError(
                    f"Grouping column '{column}' "
                    f"not found in dataset."
                )

        # --------------------------------------------------
        # Validate KPI calculation
        # --------------------------------------------------

        method = calculation["method"]
        value_column = calculation["column"]

        if method != "count" and value_column not in df.columns:
            raise ValueError(
                f"KPI column '{value_column}' "
                f"not found in dataset."
            )

        # --------------------------------------------------
        # Calculate KPI
        # --------------------------------------------------

        if method == "sum":

            if group_by:

                result = (
                    df.groupby(
                        group_by,
                        as_index=False
                    )[value_column]
                    .sum()
                    .rename(
                        columns={
                            value_column: kpi_name
                        }
                    )
                )

            else:

                result = pd.DataFrame({
                    kpi_name: [
                        df[value_column].sum()
                    ]
                })

        elif method == "mean":

            if group_by:

                result = (
                    df.groupby(
                        group_by,
                        as_index=False
                    )[value_column]
                    .mean()
                    .rename(
                        columns={
                            value_column: kpi_name
                        }
                    )
                )

            else:

                result = pd.DataFrame({
                    kpi_name: [
                        df[value_column].mean()
                    ]
                })

        elif method == "count":

            if group_by:

                result = (
                    df.groupby(group_by)
                    .size()
                    .reset_index(
                        name=kpi_name
                    )
                )

            else:

                result = pd.DataFrame({
                    kpi_name: [len(df)]
                })

        else:

            raise ValueError(
                f"Unsupported KPI calculation method: {method}"
            )

        # --------------------------------------------------
        # Sort output
        # --------------------------------------------------

        if group_by:

            result = result.sort_values(
                by=group_by
            ).reset_index(drop=True)

        return result