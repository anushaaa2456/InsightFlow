from pathlib import Path
import json
import numpy as np
import pandas as pd


# ============================================================
# 1. CONFIGURATION
# ============================================================

SEED = 42
rng = np.random.default_rng(SEED)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

RAW_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = "2026-03-01"
END_DATE = "2026-08-31"

DATES = pd.date_range(START_DATE, END_DATE, freq="D")

REGIONS = [
    "Region A",
    "Region B",
    "Region C",
    "Region D",
]

CHANNELS = [
    "Online",
    "Store",
]

CUSTOMER_SEGMENTS = [
    "Premium",
    "Regular",
    "Budget",
]


# ============================================================
# 2. PRODUCT MASTER
# ============================================================

products = []

product_counter = 1

for category, base_price_range, n_products in [
    ("Premium", (180, 350), 10),
    ("Standard", (80, 180), 12),
    ("Value", (30, 80), 8),
]:
    for _ in range(n_products):
        products.append(
            {
                "product_id": f"P{product_counter:03d}",
                "product_category": category,
                "base_price": round(
                    rng.uniform(*base_price_range), 2
                ),
            }
        )

        product_counter += 1

products_df = pd.DataFrame(products)


# ============================================================
# 3. CUSTOMER MASTER
# ============================================================

customers = []

customer_counter = 1

for region in REGIONS:

    # 300 customers per region
    for _ in range(1000):

        segment = rng.choice(
            CUSTOMER_SEGMENTS,
            p=[0.20, 0.55, 0.25],
        )

        customers.append(
            {
                "customer_id": f"C{customer_counter:05d}",
                "region": region,
                "customer_segment": segment,
                "acquisition_date": rng.choice(DATES[:120]),
            }
        )

        customer_counter += 1

customers_df = pd.DataFrame(customers)


# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================

def seasonality_multiplier(date):
    """
    Stable baseline for the prototype.
    We intentionally avoid strong synthetic seasonality
    because the primary test case is a regional anomaly.
    """

    return 1.0


def get_customer_activity_factor(region, date):
    """
    Controls active customer volume.

    Region A experiences a moderate deterioration
    during August.
    """
    if region == "Region A" and date >= pd.Timestamp("2026-08-01"):
        return 0.98

    return 1.0


def get_frequency_factor(region, date):
    """
    Controls orders per active customer.
    """
    if region == "Region A" and date >= pd.Timestamp("2026-08-01"):
        return 0.995

    return 1.0


def get_product_mix(region, date):
    """
    Region A experiences a moderate shift away
    from premium products during August.
    """

    if region == "Region A" and date >= pd.Timestamp("2026-08-01"):
        return {
            "Premium": 0.18,
            "Standard": 0.56,
            "Value": 0.26,
        }

    return {
        "Premium": 0.20,
        "Standard": 0.55,
        "Value": 0.25,
    }


def get_discount(region, date):
    """
    Slightly higher discounting during the problem period.
    """
    if region == "Region A" and date >= pd.Timestamp("2026-08-01"):
        return rng.uniform(0.08, 0.16)

    return rng.uniform(0.05, 0.10)


def get_inventory_factor(region, product_category, date):
    """
    Inventory availability.

    Premium products in Region A experience stockouts
    during August.
    """

    if (
        region == "Region A"
        and product_category == "Premium"
        and date >= pd.Timestamp("2026-08-01")
    ):
        return 0.88

    return rng.uniform(0.94, 0.99)


# ============================================================
# 5. GENERATE TRANSACTIONS
# ============================================================

transaction_rows = []

for date in DATES:

    seasonality = seasonality_multiplier(date)

    for region in REGIONS:

        region_customers = customers_df[
            customers_df["region"] == region
        ]

        customer_factor = get_customer_activity_factor(
            region,
            date,
        )

        frequency_factor = get_frequency_factor(
            region,
            date,
        )

        mix_probabilities = get_product_mix(
            region,
            date,
        )

        for _, customer in region_customers.iterrows():

            # Base probability of purchasing
            base_probability = 0.15

            # Customer segment effect
            segment_multiplier = {
                "Premium": 1.35,
                "Regular": 1.00,
                "Budget": 0.80,
            }[customer["customer_segment"]]

            purchase_probability = (
                base_probability
                * seasonality
                * segment_multiplier
                * customer_factor
            )

            if rng.random() > purchase_probability:
                continue

            # Orders per active customer
            expected_orders = (
                1.05
                * frequency_factor
            )

            number_of_orders = max(
                1,
                rng.poisson(expected_orders),
            )

            for _ in range(number_of_orders):

                # Select product category
                category = rng.choice(
                    list(mix_probabilities.keys()),
                    p=list(mix_probabilities.values()),
                )

                category_products = products_df[
                    products_df["product_category"] == category
                ]

                product = category_products.sample(
                    n=1,
                    random_state=int(rng.integers(0, 1_000_000)),
                ).iloc[0]

                base_price = product["base_price"]

                discount = get_discount(
                    region,
                    date,
                )

                price = base_price * (1 - discount)

                units = int(
                    rng.choice(
                        [1, 2, 3],
                        p=[0.78, 0.18, 0.04],
                    )
                )

                revenue = price * units

                channel = rng.choice(
                    CHANNELS,
                    p=[0.55, 0.45],
                )

                transaction_rows.append(
                    {
                        "date": date,
                        "region": region,
                        "channel": channel,
                        "customer_id": customer["customer_id"],
                        "product_id": product["product_id"],
                        "product_category": product[
                            "product_category"
                        ],
                        "customer_segment": customer[
                            "customer_segment"
                        ],
                        "orders": 1,
                        "units": units,
                        "revenue": round(revenue, 2),
                        "price": round(price, 2),
                        "discount": round(discount, 4),
                    }
                )


transactions_df = pd.DataFrame(transaction_rows)


# ============================================================
# 6. GENERATE OPERATIONS / INVENTORY DATA
# ============================================================

operation_rows = []

for date in DATES:

    for region in REGIONS:

        for _, product in products_df.iterrows():

            inventory_factor = get_inventory_factor(
                region,
                product["product_category"],
                date,
            )

            capacity = int(
                rng.integers(80, 160)
            )

            available = int(
                capacity * inventory_factor
            )

            stockout_hours = max(
                0,
                round(
                    (1 - inventory_factor) * 24
                    + rng.normal(0, 0.5),
                    2,
                ),
            )

            operation_rows.append(
                {
                    "date": date,
                    "region": region,
                    "product_id": product[
                        "product_id"
                    ],
                    "inventory_available": available,
                    "inventory_capacity": capacity,
                    "stockout_hours": stockout_hours,
                }
            )


operations_df = pd.DataFrame(operation_rows)


# ============================================================
# 7. GENERATE UNSTRUCTURED BUSINESS CONTEXT
# ============================================================

business_context = []

def add_context(
    date,
    region,
    source_type,
    source,
    text,
    product_category=None,
):

    business_context.append(
        {
            "date": str(date.date()),
            "region": region,
            "product_category": product_category,
            "source_type": source_type,
            "source": source,
            "text": text,
        }
    )


# ---- Region A: premium availability evidence ----

for date in pd.date_range(
    "2026-08-05",
    "2026-08-25",
    freq="4D",
):

    add_context(
        date=date,
        region="Region A",
        source_type="customer_review",
        source="Customer Review",
        product_category="Premium",
        text=(
            "Customers reported difficulty finding "
            "premium products in stock."
        ),
    )


# ---- Region A: competitor pricing evidence ----

add_context(
    date=pd.Timestamp("2026-08-08"),
    region="Region A",
    source_type="competitor_news",
    source="Market Intelligence",
    product_category="Premium",
    text=(
        "Competitor X reduced prices on comparable "
        "premium products by approximately 10%."
    ),
)


add_context(
    date=pd.Timestamp("2026-08-12"),
    region="Region A",
    source_type="sales_note",
    source="Regional Sales Team",
    product_category="Premium",
    text=(
        "Sales representatives reported customers "
        "mentioning competitor pricing during purchase discussions."
    ),
)


# ---- Inventory-related sales notes ----

add_context(
    date=pd.Timestamp("2026-08-15"),
    region="Region A",
    source_type="sales_note",
    source="Regional Sales Team",
    product_category="Premium",
    text=(
        "Several premium SKUs were unavailable during "
        "customer purchase attempts."
    ),
)


# ---- Control regions: neutral context ----

add_context(
    date=pd.Timestamp("2026-08-10"),
    region="Region B",
    source_type="sales_note",
    source="Regional Sales Team",
    text=(
        "Sales activity remained broadly stable "
        "during the reporting period."
    ),
)

add_context(
    date=pd.Timestamp("2026-08-10"),
    region="Region C",
    source_type="customer_review",
    source="Customer Review",
    text=(
        "Customers reported generally positive "
        "product availability."
    ),
)


business_context_df = pd.DataFrame(
    business_context
)


# ============================================================
# 8. SAVE DATASETS
# ============================================================

transactions_path = RAW_DIR / "transactions.csv"
operations_path = RAW_DIR / "operations.csv"
context_path = RAW_DIR / "business_context.json"

transactions_df.to_csv(
    transactions_path,
    index=False,
)

operations_df.to_csv(
    operations_path,
    index=False,
)

with open(
    context_path,
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        business_context,
        f,
        indent=2,
        ensure_ascii=False,
    )


# ============================================================
# 9. BASIC SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("INSIGHTFLOW DATA GENERATION COMPLETE")
print("=" * 60)

print(
    f"\nTransactions: "
    f"{len(transactions_df):,} rows"
)

print(
    f"Operations:   "
    f"{len(operations_df):,} rows"
)

print(
    f"Context:      "
    f"{len(business_context_df):,} records"
)

print("\nDate range:")
print(
    transactions_df["date"].min(),
    "→",
    transactions_df["date"].max(),
)

print("\nRevenue by region:")

region_revenue = (
    transactions_df
    .groupby("region")["revenue"]
    .sum()
    .sort_values(ascending=False)
)

print(region_revenue)

print("\nFiles created:")

print(transactions_path)
print(operations_path)
print(context_path)

print("\n" + "=" * 60)