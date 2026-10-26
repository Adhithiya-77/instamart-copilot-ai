import sqlite3
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "outputs" / "instamart.db"

# Connect to database
connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

print("=" * 55)
print("ORDER AMOUNT QUALITY ANALYSIS")
print("=" * 55)

# 1. Analyze all orders
cursor.execute("""
    SELECT
        COUNT(*) AS total_orders,
        SUM(
            CASE
                WHEN order_amount IS NULL THEN 1
                ELSE 0
            END
        ) AS missing_amounts,
        SUM(
            CASE
                WHEN order_amount IS NOT NULL THEN 1
                ELSE 0
            END
        ) AS available_amounts
    FROM orders
""")

total, missing, available = cursor.fetchone()

missing = missing or 0
available = available or 0

missing_percentage = (
    (missing / total) * 100 if total else 0
)

print("\nALL ORDERS")
print("-" * 40)
print("Total orders:", total)
print("Orders with missing amounts:", missing)
print("Orders with recorded amounts:", available)
print(f"Missing amount percentage: {missing_percentage:.2f}%")

# 2. Analyze completed orders
cursor.execute("""
    SELECT
        COUNT(*),
        SUM(
            CASE
                WHEN order_amount IS NULL THEN 1
                ELSE 0
            END
        )
    FROM orders
    WHERE LOWER(TRIM(status)) = 'completed'
""")

completed_total, completed_missing = cursor.fetchone()

completed_missing = completed_missing or 0

completed_percentage = (
    (completed_missing / completed_total) * 100
    if completed_total else 0
)

print("\nCOMPLETED ORDERS")
print("-" * 40)
print("Total completed orders:", completed_total)
print("Missing amounts:", completed_missing)
print(f"Missing percentage: {completed_percentage:.2f}%")

# 3. Summarize recorded amounts
cursor.execute("""
    SELECT
        MIN(order_amount),
        MAX(order_amount),
        AVG(order_amount)
    FROM orders
    WHERE order_amount IS NOT NULL
""")

minimum, maximum, average = cursor.fetchone()

print("\nRECORDED ORDER AMOUNTS")
print("-" * 40)
print("Minimum amount:", minimum)
print("Maximum amount:", maximum)
print(
    "Average amount:",
    round(average, 2) if average is not None else None
)

connection.close()

print("\nAnalysis completed successfully!")