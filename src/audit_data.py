import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

# Load datasets
customers = pd.read_csv(RAW_DIR / "customers.csv")
products = pd.read_csv(RAW_DIR / "products.csv")
orders = pd.read_csv(RAW_DIR / "orders.csv")
tickets = pd.read_csv(RAW_DIR / "tickets.csv", keep_default_na=False)

datasets = {
    "Customers": customers,
    "Products": products,
    "Orders": orders,
    "Tickets": tickets
}

# Display basic information
for name, df in datasets.items():
    print("\n" + "=" * 60)
    print(f"{name.upper()} DATASET")
    print("=" * 60)

    print(f"Shape: {df.shape}")

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    missing = pd.DataFrame({
        "Missing Count": df.isna().sum(),
        "Missing Percentage": (df.isna().mean() * 100).round(2)
    })
    print(missing)

# Orders audit
print("\n" + "=" * 60)
print("ORDERS AUDIT")
print("=" * 60)

print("Total rows:", len(orders))
print("Exact duplicate rows:", orders.duplicated().sum())
print("Pending rows:", (orders["status"] == "pending").sum())
print("Distinct order IDs:", orders["order_id"].nunique())

numeric_amount = pd.to_numeric(orders["order_amount"], errors="coerce")

print("Non-numeric order amounts:", numeric_amount.isna().sum())

delivery = pd.to_numeric(orders["delivery_minutes"], errors="coerce")

print("Negative delivery times:", (delivery < 0).sum())
print("Blank delivery times:", orders["delivery_minutes"].isna().sum()
      + (orders["delivery_minutes"].astype(str).str.strip() == "").sum())

# Customer audit
print("\n" + "=" * 60)
print("CUSTOMERS AUDIT")
print("=" * 60)

ages = pd.to_numeric(customers["age"], errors="coerce")

print("Blank ages:", customers["age"].isna().sum()
      + (customers["age"].astype(str).str.strip() == "").sum())

print("Ages outside 10-100:", ((ages < 10) | (ages > 100)).sum())

print("Distinct raw city spellings:", customers["city"].nunique())

gender = customers["gender"].astype(str).str.strip()

print(
    "Distinct non-blank gender spellings:",
    gender[gender != ""].nunique()
)

print("Blank genders:", customers["gender"].isna().sum()
      + (gender == "").sum())

print("\nAudit completed successfully!")