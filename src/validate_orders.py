import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_DIR = BASE_DIR / "data" / "clean"

# Load cleaned orders
orders = pd.read_csv(
    CLEAN_DIR / "orders.csv",
    keep_default_na=False
)

print("=" * 50)
print("CLEANED ORDERS VALIDATION")
print("=" * 50)

# 1. Dataset size
print("\nTotal rows:", len(orders))
print("Total columns:", len(orders.columns))

# 2. Check duplicate records
print("\nExact duplicate rows:", orders.duplicated().sum())

if "order_id" in orders.columns:
    print("Duplicate order IDs:", orders["order_id"].duplicated().sum())

# 3. Check order amounts
if "order_amount" in orders.columns:
    amounts = pd.to_numeric(
        orders["order_amount"].replace("", pd.NA),
        errors="coerce"
    )

    print("\nOrder amount missing/invalid:", amounts.isna().sum())
    print("Non-positive order amounts:", (amounts <= 0).sum())
    print("Minimum valid amount:", amounts.min())
    print("Maximum valid amount:", amounts.max())

# 4. Check delivery times
if "delivery_minutes" in orders.columns:
    delivery = pd.to_numeric(
        orders["delivery_minutes"].replace("", pd.NA),
        errors="coerce"
    )

    print("\nMissing delivery times:", delivery.isna().sum())
    print("Negative delivery times:", (delivery < 0).sum())
    print("Minimum delivery time:", delivery.min())
    print("Maximum delivery time:", delivery.max())

# 5. Check statuses
if "status" in orders.columns:
    print("\nOrder status counts:")
    print(orders["status"].value_counts(dropna=False))

# 6. Check customer IDs
if "customer_id" in orders.columns:
    print("\nMissing customer IDs:", (orders["customer_id"] == "").sum())

# 7. Check product IDs
if "product_id" in orders.columns:
    print("Missing product IDs:", (orders["product_id"] == "").sum())

print("\nValidation completed!")