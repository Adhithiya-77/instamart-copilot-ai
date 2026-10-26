import sqlite3
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "outputs" / "instamart.db"

# Connect to SQLite database
connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

print("=" * 50)
print("DATABASE INTEGRITY VALIDATION")
print("=" * 50)

# 1. Check table row counts
for table in ["customers", "products", "orders"]:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"{table.capitalize()} count: {cursor.fetchone()[0]}")

# 2. Check whether order customer IDs exist
cursor.execute("""
    SELECT COUNT(*)
    FROM orders o
    LEFT JOIN customers c
        ON o.customer_id = c.customer_id
    WHERE c.customer_id IS NULL
""")

missing_customers = cursor.fetchone()[0]
print("\nOrders with invalid customer IDs:", missing_customers)

# 3. Check whether order product IDs exist
cursor.execute("""
    SELECT COUNT(*)
    FROM orders o
    LEFT JOIN products p
        ON o.product_id = p.product_id
    WHERE p.product_id IS NULL
""")

missing_products = cursor.fetchone()[0]
print("Orders with invalid product IDs:", missing_products)

# 4. Check duplicate order IDs
cursor.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT order_id
        FROM orders
        GROUP BY order_id
        HAVING COUNT(*) > 1
    )
""")

duplicate_ids = cursor.fetchone()[0]
print("Order IDs appearing multiple times:", duplicate_ids)

# 5. Check product prices
cursor.execute("""
    SELECT
        COUNT(*),
        MIN(price_inr),
        MAX(price_inr)
    FROM products
""")

result = cursor.fetchone()

print("\nProduct price summary:")
print("Product count:", result[0])
print("Minimum price:", result[1])
print("Maximum price:", result[2])

# 6. Check completed orders with missing amounts
cursor.execute("""
    SELECT COUNT(*)
    FROM orders
    WHERE LOWER(TRIM(status)) = 'completed'
      AND (
          order_amount IS NULL
          OR TRIM(CAST(order_amount AS TEXT)) = ''
      )
""")

missing_completed_amounts = cursor.fetchone()[0]

print(
    "\nCompleted orders with missing amounts:",
    missing_completed_amounts
)

connection.close()

print("\nDatabase validation completed!")