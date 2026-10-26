import sqlite3
import pandas as pd
from pathlib import Path

# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_DIR = BASE_DIR / "data" / "clean"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = OUTPUT_DIR / "instamart.db"


# ==========================================
# 2. LOAD CLEANED DATASETS
# ==========================================

customers = pd.read_csv(CLEAN_DIR / "customers.csv")
products = pd.read_csv(CLEAN_DIR / "products.csv")
orders = pd.read_csv(CLEAN_DIR / "orders.csv")

print("Customers loaded:", len(customers))
print("Products loaded:", len(products))
print("Orders loaded:", len(orders))


# ==========================================
# 3. CREATE SQLITE DATABASE
# ==========================================

with sqlite3.connect(DB_PATH) as connection:

    # Create database tables from DataFrames
    customers.to_sql(
        "customers",
        connection,
        if_exists="replace",
        index=False
    )

    products.to_sql(
        "products",
        connection,
        if_exists="replace",
        index=False
    )

    orders.to_sql(
        "orders",
        connection,
        if_exists="replace",
        index=False
    )

    # ==========================================
    # 4. VERIFY TABLES
    # ==========================================

    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """)

    print("\nDatabase tables:")

    for row in cursor.fetchall():
        print("-", row[0])

    # ==========================================
    # 5. VERIFY ROW COUNTS
    # ==========================================

    print("\nDatabase row counts:")

    for table in ["customers", "products", "orders"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]

        print(f"{table}: {count}")

    # ==========================================
    # 6. PREVIEW REVENUE
    # ==========================================

    cursor.execute("""
        SELECT
            status,
            COUNT(*) AS order_count
        FROM orders
        GROUP BY status
        ORDER BY status
    """)

    print("\nOrder status summary:")

    for row in cursor.fetchall():
        print(row)


# ==========================================
# 7. COMPLETION MESSAGE
# ==========================================

print("\nDatabase created successfully!")
print("Database location:", DB_PATH)