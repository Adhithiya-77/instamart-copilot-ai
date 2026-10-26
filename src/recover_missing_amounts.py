import sqlite3
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "outputs" / "instamart.db"

# Connect to database
connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

print("=" * 60)
print("MISSING AMOUNT RECOVERY ANALYSIS")
print("=" * 60)

# Inspect the product table columns
cursor.execute("PRAGMA table_info(products)")
product_columns = [column[1] for column in cursor.fetchall()]

print("\nProduct table columns:", product_columns)

# Inspect the order table columns
cursor.execute("PRAGMA table_info(orders)")
order_columns = [column[1] for column in cursor.fetchall()]

print("Order table columns:", order_columns)

# Display missing-amount orders and their product details
cursor.execute("""
    SELECT
        o.order_id,
        o.product_id,
        o.quantity,
        o.order_amount,
        p.product_name,
        p.price_inr
    FROM orders AS o
    LEFT JOIN products AS p
        ON o.product_id = p.product_id
    WHERE LOWER(TRIM(o.status)) = 'completed'
      AND o.order_amount IS NULL
    LIMIT 10
""")

rows = cursor.fetchall()

print("\nSample orders with missing amounts:\n")

for row in rows:
    order_id, product_id, quantity, amount, product_name, price = row

    print("-" * 50)
    print("Order ID:", order_id)
    print("Product ID:", product_id)
    print("Quantity:", quantity)
    print("Recorded amount:", amount)
    print("Product name:", product_name)
    print("Product price:", price)

    if price is not None and quantity is not None:
        print("Quantity × product price:", quantity * price)

connection.close()

print("\nAnalysis completed!")