import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

# Load raw orders
orders = pd.read_csv(
    RAW_DIR / "orders.csv",
    dtype=str,
    keep_default_na=False
)

print("=" * 50)
print("RAW ORDERS DATA INSPECTION")
print("=" * 50)

# Dataset information
print("\nTotal rows:", len(orders))
print("Total columns:", len(orders.columns))

print("\nColumn names:")
print(orders.columns.tolist())

print("\nFirst five rows:")
print(orders.head().to_string(index=False))

# Exact duplicate rows
print("\nExact duplicate rows:", orders.duplicated().sum())

# Duplicate order IDs
if "order_id" in orders.columns:
    print(
        "Duplicate order IDs:",
        orders["order_id"].duplicated().sum()
    )

# Check numeric columns
for column in ["order_amount", "delivery_minutes"]:
    if column in orders.columns:
        values = pd.to_numeric(
            orders[column].replace("", pd.NA),
            errors="coerce"
        )

        print(f"\n{column} inspection:")
        print("Missing or invalid:", values.isna().sum())
        print("Minimum:", values.min())
        print("Maximum:", values.max())
        print("Negative values:", (values < 0).sum())
        print("Zero values:", (values == 0).sum())

# Check order status
if "status" in orders.columns:
    print("\nOrder status counts:")
    print(orders["status"].value_counts(dropna=False).to_string())

# Check missing values
print("\nBlank values by column:")

for column in orders.columns:
    blank_count = (
        orders[column].astype(str).str.strip() == ""
    ).sum()

    if blank_count > 0:
        print(f"{column}: {blank_count}")

print("\nInspection completed!")