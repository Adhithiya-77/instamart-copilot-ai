import sqlite3
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "outputs" / "instamart.db"

# Connect to database
connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

print("=" * 60)
print("MISSING ORDER AMOUNT INVESTIGATION")
print("=" * 60)

# 1. Count completed orders with missing amounts
cursor.execute("""
    SELECT COUNT(*)
    FROM orders
    WHERE LOWER(TRIM(status)) = 'completed'
      AND (
          order_amount IS NULL
          OR TRIM(CAST(order_amount AS TEXT)) = ''
      )
""")

missing_count = cursor.fetchone()[0]

print("\nCompleted orders with missing amounts:", missing_count)

# 2. Display affected orders
cursor.execute("""
    SELECT
        order_id,
        customer_id,
        product_id,
        quantity,
        order_ts,
        status,
        order_amount,
        delivery_minutes
    FROM orders
    WHERE LOWER(TRIM(status)) = 'completed'
      AND (
          order_amount IS NULL
          OR TRIM(CAST(order_amount AS TEXT)) = ''
      )
    LIMIT 10
""")

rows = cursor.fetchall()

print("\nFirst 10 affected orders:\n")

if rows:
    for row in rows:
        print("-" * 50)
        print("Order ID:", row[0])
        print("Customer ID:", row[1])
        print("Product ID:", row[2])
        print("Quantity:", row[3])
        print("Timestamp:", row[4])
        print("Status:", row[5])
        print("Order Amount:", row[6])
        print("Delivery Minutes:", row[7])
else:
    print("No affected orders found.")

# 3. Close database connection
connection.close()

print("\nInvestigation completed!")