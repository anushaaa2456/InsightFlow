from pathlib import Path

import pandas as pd

from src.kpi.registry import KPIRegistry


class KPICalculator:
    """
    Generic KPI calculation engine.

    The KPI registry defines WHAT should be calculated.
    This class defines HOW the registered calculation is executed.

    Supported calculation methods:

        sum
        mean
        count
        nunique
        ratio
    """

    SUPPORTED_METHODS = {
        "sum",
        "mean",
        "count",
        "nunique",
        "ratio",
    }

    def __init__(self, registry=None):
        self.registry = registry or KPIRegistry()

    # ==========================================================
    # DATA LOADING
    # ==========================================================

    def load_data(self, kpi_name):
        """
        Load the dataset associated with the requested KPI.
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

    # ==========================================================
    # PREPROCESSING
    # ==========================================================

    def _prepare_data(
        self,
        df,
        group_by
    ):
        """
        Prepare reporting dimensions such as month.
        """

        group_by = group_by or []

        if "date" in df.columns:

            df["date"] = pd.to_datetime(
                df["date"],
                errors="coerce"
            )

        # ------------------------------------------------------
        # Create monthly reporting dimension
        # ------------------------------------------------------

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

        return df

    # ==========================================================
    # FILTERING
    # ==========================================================

    def _apply_filters(
        self,
        df,
        filters
    ):
        """
        Apply user-provided filters.

        Example:

            {
                "region": "Region A"
            }

        or:

            {
                "region": [
                    "Region A",
                    "Region B"
                ]
            }
        """

        if not filters:
            return df

        for column, value in filters.items():

            if column not in df.columns:
                raise ValueError(
                    f"Filter column '{column}' "
                    f"not found in dataset."
                )

            if isinstance(value, list):

                df = df[
                    df[column].isin(value)
                ]

            else:

                df = df[
                    df[column] == value
                ]

        return df

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def _validate_grouping_columns(
        self,
        df,
        group_by
    ):
        """
        Ensure requested dimensions exist.
        """

        for column in group_by:

            if column not in df.columns:
                raise ValueError(
                    f"Grouping column '{column}' "
                    f"not found in dataset."
                )

    def _validate_calculation(
        self,
        df,
        calculation
    ):
        """
        Validate the calculation configuration against
        the actual dataset.
        """

        method = calculation["method"]

        if method not in self.SUPPORTED_METHODS:

            raise ValueError(
                f"Unsupported KPI calculation method: "
                f"{method}. "
                f"Supported methods: "
                f"{sorted(self.SUPPORTED_METHODS)}"
            )

        # ------------------------------------------------------
        # Methods requiring a single source column
        # ------------------------------------------------------

        if method in {
            "sum",
            "mean",
            "nunique",
        }:

            column = calculation.get("column")

            if not column:
                raise ValueError(
                    f"Calculation method '{method}' "
                    f"requires a 'column'."
                )

            if column not in df.columns:
                raise ValueError(
                    f"KPI column '{column}' "
                    f"not found in dataset."
                )

        # ------------------------------------------------------
        # Ratio calculation
        # ------------------------------------------------------

        elif method == "ratio":

            numerator = calculation.get(
                "numerator"
            )

            denominator = calculation.get(
                "denominator"
            )

            if not numerator or not denominator:

                raise ValueError(
                    "Ratio calculation requires "
                    "'numerator' and 'denominator'."
                )

            if numerator not in df.columns:

                raise ValueError(
                    f"Ratio numerator '{numerator}' "
                    f"not found in dataset."
                )

            if denominator not in df.columns:

                raise ValueError(
                    f"Ratio denominator '{denominator}' "
                    f"not found in dataset."
                )

    # ==========================================================
    # AGGREGATION HELPERS
    # ==========================================================

    def _aggregate_sum(
        self,
        df,
        column,
        group_by,
        output_name
    ):
        """
        Sum a column.
        """

        if group_by:

            return (
                df.groupby(
                    group_by,
                    as_index=False
                )[column]
                .sum()
                .rename(
                    columns={
                        column: output_name
                    }
                )
            )

        return pd.DataFrame({
            output_name: [
                df[column].sum()
            ]
        })

    def _aggregate_mean(
        self,
        df,
        column,
        group_by,
        output_name
    ):
        """
        Calculate mean of a column.
        """

        if group_by:

            return (
                df.groupby(
                    group_by,
                    as_index=False
                )[column]
                .mean()
                .rename(
                    columns={
                        column: output_name
                    }
                )
            )

        return pd.DataFrame({
            output_name: [
                df[column].mean()
            ]
        })

    def _aggregate_count(
        self,
        df,
        group_by,
        output_name
    ):
        """
        Count rows.
        """

        if group_by:

            return (
                df.groupby(group_by)
                .size()
                .reset_index(
                    name=output_name
                )
            )

        return pd.DataFrame({
            output_name: [
                len(df)
            ]
        })

    def _aggregate_nunique(
        self,
        df,
        column,
        group_by,
        output_name
    ):
        """
        Count unique values.
        """

        if group_by:

            return (
                df.groupby(
                    group_by,
                    as_index=False
                )[column]
                .nunique()
                .rename(
                    columns={
                        column: output_name
                    }
                )
            )

        return pd.DataFrame({
            output_name: [
                df[column].nunique()
            ]
        })

    def _aggregate_ratio(
        self,
        df,
        numerator,
        denominator,
        group_by,
        output_name
    ):
        """
        Calculate a ratio using aggregated numerator
        and denominator.

        IMPORTANT:

            ratio = SUM(numerator) / SUM(denominator)

        rather than:

            mean(numerator / denominator)

        This prevents row-level weighting from distorting
        KPIs such as AOV.
        """

        if group_by:

            grouped = (
                df.groupby(
                    group_by,
                    as_index=False
                )
                .agg(
                    numerator_value=(
                        numerator,
                        "sum"
                    ),
                    denominator_value=(
                        denominator,
                        "sum"
                    )
                )
            )

            grouped[output_name] = (
                grouped["numerator_value"]
                / grouped["denominator_value"]
            )

            return grouped[
                group_by + [output_name]
            ]

        denominator_value = df[
            denominator
        ].sum()

        if denominator_value == 0:

            ratio = None

        else:

            ratio = (
                df[numerator].sum()
                / denominator_value
            )

        return pd.DataFrame({
            output_name: [ratio]
        })

    # ==========================================================
    # MAIN CALCULATION
    # ==========================================================

    def calculate(
        self,
        kpi_name,
        group_by=None,
        filters=None
    ):
        """
        Calculate any registered KPI.

        Parameters
        ----------
        kpi_name : str
            Registered KPI name.

        group_by : list[str], optional
            Dimensions by which to aggregate.

            Examples:

                ["region"]

                ["region", "month"]

                ["region", "product_category"]

        filters : dict, optional
            Column-value filters.

            Examples:

                {"region": "Region A"}

                {
                    "region": [
                        "Region A",
                        "Region B"
                    ]
                }

        Returns
        -------
        pandas.DataFrame
            Calculated KPI values.
        """

        group_by = group_by or []

        # ------------------------------------------------------
        # Get semantic definition
        # ------------------------------------------------------

        kpi_config = self.registry.get(
            kpi_name
        )

        calculation = (
            self.registry.get_calculation(
                kpi_name
            )
        )

        # ------------------------------------------------------
        # Load data
        # ------------------------------------------------------

        df = self.load_data(
            kpi_name
        )

        # ------------------------------------------------------
        # Prepare reporting dimensions
        # ------------------------------------------------------

        df = self._prepare_data(
            df,
            group_by
        )

        # ------------------------------------------------------
        # Apply filters
        # ------------------------------------------------------

        df = self._apply_filters(
            df,
            filters
        )

        # ------------------------------------------------------
        # Validate requested dimensions
        # ------------------------------------------------------

        self._validate_grouping_columns(
            df,
            group_by
        )

        # ------------------------------------------------------
        # Validate calculation
        # ------------------------------------------------------

        self._validate_calculation(
            df,
            calculation
        )

        # ------------------------------------------------------
        # Output KPI name
        # ------------------------------------------------------

        output_name = kpi_name

        method = calculation["method"]

        # ------------------------------------------------------
        # Execute calculation
        # ------------------------------------------------------

        if method == "sum":

            result = self._aggregate_sum(
                df=df,
                column=calculation["column"],
                group_by=group_by,
                output_name=output_name
            )

        elif method == "mean":

            result = self._aggregate_mean(
                df=df,
                column=calculation["column"],
                group_by=group_by,
                output_name=output_name
            )

        elif method == "count":

            result = self._aggregate_count(
                df=df,
                group_by=group_by,
                output_name=output_name
            )

        elif method == "nunique":

            result = self._aggregate_nunique(
                df=df,
                column=calculation["column"],
                group_by=group_by,
                output_name=output_name
            )

        elif method == "ratio":

            result = self._aggregate_ratio(
                df=df,
                numerator=calculation["numerator"],
                denominator=calculation["denominator"],
                group_by=group_by,
                output_name=output_name
            )

        else:

            # This should never be reached because
            # validation happens above.
            raise ValueError(
                f"Unsupported KPI calculation method: "
                f"{method}"
            )

        # ------------------------------------------------------
        # Sort grouped results
        # ------------------------------------------------------

        if group_by:

            result = (
                result
                .sort_values(
                    by=group_by
                )
                .reset_index(
                    drop=True
                )
            )

        return result