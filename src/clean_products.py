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
# 2. LOAD PRODUCT DATA
# ==========================================

input_file = RAW_DIR / "products.csv"
products = pd.read_csv(input_file)

print("=" * 50)
print("PRODUCT DATA CLEANING")
print("=" * 50)

print("\nOriginal product count:", len(products))
print("\nOriginal column names:")
print(products.columns.tolist())

print("\nOriginal data:")
print(products.head())


# ==========================================
# 3. CLEAN COLUMN NAMES
# ==========================================

products.columns = (
    products.columns
    .str.strip()
    .str.lower()
)

# Remove surrounding whitespace from text columns
for column in products.select_dtypes(include=["object", "string"]).columns:
    products[column] = products[column].str.strip()


# ==========================================
# 4. STANDARDIZE CATEGORY
# ==========================================

if "category" in products.columns:
    products["category"] = (
        products["category"]
        .astype("string")
        .str.strip()
        .str.title()
    )


# ==========================================
# 5. CHECK PRODUCT IDENTIFIERS
# ==========================================

if "product_id" in products.columns:
    print(
        "\nDuplicate product IDs:",
        products["product_id"].duplicated().sum()
    )
else:
    print("\nNo product_id column found.")


# ==========================================
# 6. CHECK NUMERIC COLUMNS
# ==========================================

print("\nNumeric columns available:")

numeric_columns = products.select_dtypes(
    include=["number"]
).columns.tolist()

print(numeric_columns)

# Display possible price-related columns
possible_price_columns = [
    column for column in products.columns
    if "price" in column or "amount" in column or "cost" in column
]

print("\nPossible price-related columns:")
print(possible_price_columns)


# ==========================================
# 7. REMOVE DUPLICATE PRODUCTS
# ==========================================

if "product_id" in products.columns:
    products = products.drop_duplicates(
        subset=["product_id"],
        keep="first"
    ).copy()
else:
    products = products.drop_duplicates().copy()


# ==========================================
# 8. SAVE CLEAN PRODUCT DATA
# ==========================================

output_file = CLEAN_DIR / "products.csv"

products.to_csv(
    output_file,
    index=False
)


# ==========================================
# 9. DISPLAY RESULTS
# ==========================================

print("\n" + "=" * 50)
print("PRODUCT CLEANING COMPLETED")
print("=" * 50)

print("\nFinal product count:", len(products))

print("\nMissing values:")
print(products.isna().sum())

if "category" in products.columns:
    print("\nProduct categories:")
    print(products["category"].value_counts(dropna=False))

print("\nSaved cleaned data to:")
print(output_file)