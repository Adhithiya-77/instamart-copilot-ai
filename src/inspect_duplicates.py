import sqlite3
from pathlib import Path

# Database path
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "outputs" / "instamart.db"

# Connect to database
connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

print("=" * 50)
print("DUPLICATE ORDER ID INVESTIGATION")
print("=" * 50)

# Count order IDs that appear more than once
cursor.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT order_id
        FROM orders
        GROUP BY order_id
        HAVING COUNT(*) > 1
    )
""")

duplicate_groups = cursor.fetchone()[0]

print("\nOrder IDs appearing multiple times:", duplicate_groups)

# Show the most frequently repeated order IDs
cursor.execute("""
    SELECT order_id, COUNT(*) AS occurrences
    FROM orders
    GROUP BY order_id
    HAVING COUNT(*) > 1
    ORDER BY occurrences DESC
    LIMIT 10
""")

duplicates = cursor.fetchall()

print("\nTop 10 repeated order IDs:")
for order_id, occurrences in duplicates:
    print(f"Order ID: {order_id} | Occurrences: {occurrences}")

# Display all records for the most repeated order ID
if duplicates:
    sample_order_id = duplicates[0][0]

    cursor.execute("""
        SELECT *
        FROM orders
        WHERE order_id = ?
    """, (sample_order_id,))

    records = cursor.fetchall()

    print(f"\nRecords for order ID {sample_order_id}:")
    for record in records:
        print(record)

connection.close()

print("\nInvestigation completed!")