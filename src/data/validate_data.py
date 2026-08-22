from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

transactions = pd.read_csv(
    RAW_DIR / "transactions.csv",
    parse_dates=["date"]
)

operations = pd.read_csv(
    RAW_DIR / "operations.csv",
    parse_dates=["date"]
)


# ---------------------------------------------------------
# Basic validation
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("INSIGHTFLOW DATA VALIDATION")
print("=" * 60)

print("\n1. DATASET SIZES")
print("-" * 60)

print(f"Transactions: {len(transactions):,} rows")
print(f"Operations:   {len(operations):,} rows")


print("\n2. DATE RANGE")
print("-" * 60)

print(
    f"Transactions: "
    f"{transactions['date'].min().date()} → "
    f"{transactions['date'].max().date()}"
)


print("\n3. REGIONS")
print("-" * 60)

print(
    transactions["region"]
    .value_counts()
    .sort_index()
)


# ---------------------------------------------------------
# Monthly revenue
# ---------------------------------------------------------

transactions["month"] = (
    transactions["date"]
    .dt.to_period("M")
)

monthly_revenue = (
    transactions
    .groupby(["region", "month"])["revenue"]
    .sum()
    .reset_index()
)


print("\n4. MONTHLY REVENUE — REGION A")
print("-" * 60)

region_a = monthly_revenue[
    monthly_revenue["region"] == "Region A"
]

print(region_a.to_string(index=False))


# ---------------------------------------------------------
# July vs August
# ---------------------------------------------------------

comparison = (
    monthly_revenue[
        monthly_revenue["month"].isin(
            [
                pd.Period("2026-07"),
                pd.Period("2026-08"),
            ]
        )
    ]
    .pivot(
        index="region",
        columns="month",
        values="revenue"
    )
)


comparison["change_pct"] = (
    (
        comparison[pd.Period("2026-08")]
        /
        comparison[pd.Period("2026-07")]
    ) - 1
) * 100


print("\n5. JULY → AUGUST REVENUE CHANGE")
print("-" * 60)

print(
    comparison
    .round(2)
    .to_string()
)


# ---------------------------------------------------------
# AOV
# ---------------------------------------------------------

aov = (
    transactions
    .groupby(
        ["region", "month"]
    )
    .agg(
        revenue=("revenue", "sum"),
        orders=("orders", "sum")
    )
    .reset_index()
)

aov["aov"] = (
    aov["revenue"] /
    aov["orders"]
)


region_a_aov = aov[
    (aov["region"] == "Region A") &
    (
        aov["month"].isin(
            [
                pd.Period("2026-07"),
                pd.Period("2026-08"),
            ]
        )
    )
]


print("\n6. REGION A — AOV")
print("-" * 60)

print(
    region_a_aov
    .round(2)
    .to_string(index=False)
)


# ---------------------------------------------------------
# Premium product mix
# ---------------------------------------------------------

premium = (
    transactions[
        transactions["product_category"] == "Premium"
    ]
    .groupby(
        ["region", "month"]
    )["revenue"]
    .sum()
    .reset_index()
    .rename(
        columns={
            "revenue": "premium_revenue"
        }
    )
)

total = (
    transactions
    .groupby(
        ["region", "month"]
    )["revenue"]
    .sum()
    .reset_index()
    .rename(
        columns={
            "revenue": "total_revenue"
        }
    )
)

mix = premium.merge(
    total,
    on=["region", "month"]
)

mix["premium_share"] = (
    mix["premium_revenue"]
    /
    mix["total_revenue"]
    * 100
)


region_a_mix = mix[
    (mix["region"] == "Region A") &
    (
        mix["month"].isin(
            [
                pd.Period("2026-07"),
                pd.Period("2026-08"),
            ]
        )
    )
]


print("\n7. REGION A — PREMIUM MIX")
print("-" * 60)

print(
    region_a_mix
    .round(2)
    .to_string(index=False)
)


# ---------------------------------------------------------
# Inventory availability
# ---------------------------------------------------------

operations["availability"] = (
    operations["inventory_available"]
    /
    operations["inventory_capacity"]
)


inventory_summary = (
    operations
    .groupby(
        [
            "region",
            operations["date"].dt.to_period("M")
        ]
    )["availability"]
    .mean()
    .reset_index()
    .rename(
        columns={
            "date": "month"
        }
    )
)


region_a_inventory = inventory_summary[
    (inventory_summary["region"] == "Region A") &
    (
        inventory_summary["month"].isin(
            [
                pd.Period("2026-07"),
                pd.Period("2026-08"),
            ]
        )
    )
]


print("\n8. REGION A — INVENTORY AVAILABILITY")
print("-" * 60)

print(
    region_a_inventory
    .round(3)
    .to_string(index=False)
)


# ---------------------------------------------------------
# Data quality
# ---------------------------------------------------------

print("\n9. DATA QUALITY")
print("-" * 60)

print(
    f"Missing transaction values: "
    f"{transactions.isna().sum().sum()}"
)

print(
    f"Missing operation values: "
    f"{operations.isna().sum().sum()}"
)

print(
    f"Negative revenue rows: "
    f"{(transactions['revenue'] < 0).sum()}"
)

print(
    f"Invalid inventory rows: "
    f"{(operations['inventory_available'] < 0).sum()}"
)


print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)