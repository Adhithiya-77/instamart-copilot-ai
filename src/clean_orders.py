import pandas as pd
from pathlib import Path

# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "clean"

CLEAN_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 2. LOAD RAW ORDERS
# ==========================================

orders = pd.read_csv(
    RAW_DIR / "orders.csv",
    dtype=str,
    keep_default_na=False
)

print("=" * 50)
print("ORDERS DATA CLEANING")
print("=" * 50)

print("Original rows:", len(orders))


# ==========================================
# 3. CLEAN COLUMN NAMES AND TEXT
# ==========================================

orders.columns = (
    orders.columns
    .str.strip()
    .str.lower()
)

for column in orders.select_dtypes(include=["object", "string"]).columns:
    orders[column] = orders[column].str.strip()


# ==========================================
# 4. REMOVE EXACT DUPLICATES
# ==========================================

duplicate_count = orders.duplicated().sum()

print("\nExact duplicate rows:", duplicate_count)

orders = orders.drop_duplicates().copy()

print("Rows after deduplication:", len(orders))


# ==========================================
# 5. STANDARDIZE ORDER STATUS
# ==========================================

if "status" in orders.columns:
    orders["status"] = orders["status"].str.lower()


# ==========================================
# 6. CONVERT NUMERIC COLUMNS
# ==========================================

for column in ["order_amount", "delivery_minutes"]:
    if column in orders.columns:
        orders[column] = pd.to_numeric(
            orders[column].replace("", pd.NA),
            errors="coerce"
        )


# ==========================================
# 7. IDENTIFY INVALID ORDER AMOUNTS
# ==========================================

if "order_amount" in orders.columns:
    invalid_amounts = (
        orders["order_amount"].isna()
        | (orders["order_amount"] <= 0)
    )

    print("\nInvalid order amounts:", invalid_amounts.sum())

    # Preserve the records for investigation.
    # Do not invent missing order amounts.


# ==========================================
# 8. IDENTIFY INVALID DELIVERY TIMES
# ==========================================

if "delivery_minutes" in orders.columns:
    negative_delivery = orders["delivery_minutes"] < 0

    print(
        "Negative delivery times:",
        negative_delivery.sum()
    )

    # Negative delivery times are invalid.
    # Replace them with missing values.
    orders.loc[negative_delivery, "delivery_minutes"] = pd.NA

    print(
        "Missing delivery times after cleaning:",
        orders["delivery_minutes"].isna().sum()
    )


# ==========================================
# 9. CHECK ORDER IDENTIFIERS
# ==========================================

if "order_id" in orders.columns:
    print(
        "\nDuplicate order IDs:",
        orders["order_id"].duplicated().sum()
    )


# ==========================================
# 10. DISPLAY MISSING VALUES
# ==========================================

print("\nMissing values by column:")
print(orders.isna().sum())


# ==========================================
# 11. SAVE CLEANED DATA
# ==========================================

output_file = CLEAN_DIR / "orders.csv"

orders.to_csv(
    output_file,
    index=False
)


# ==========================================
# 12. DISPLAY RESULTS
# ==========================================

print("\n" + "=" * 50)
print("ORDERS CLEANING COMPLETED")
print("=" * 50)

print("Final rows:", len(orders))

if "status" in orders.columns:
    print("\nOrder status counts:")
    print(orders["status"].value_counts(dropna=False))

print("\nSaved cleaned orders to:")
print(output_file)