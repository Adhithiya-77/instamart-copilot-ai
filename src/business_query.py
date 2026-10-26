import sqlite3
from pathlib import Path

# Database path
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "outputs" / "instamart.db"


def get_connection():
    """Connect to the Instamart SQLite database."""
    return sqlite3.connect(DB_PATH)


def execute_query(query, params=()):
    """Execute an SQL query and return its results."""
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()

        columns = [
            description[0]
            for description in cursor.description
        ] if cursor.description else []

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows)
        }

    finally:
        connection.close()


def get_order_summary():
    """Get the number of orders in each status."""
    return execute_query(
        """
        SELECT status, COUNT(*) AS total_orders
        FROM orders
        GROUP BY status
        ORDER BY total_orders DESC
        """
    )


def get_top_customers(limit=5):
    """Get customers with the most orders."""
    return execute_query(
        """
        SELECT customer_id, COUNT(*) AS order_count
        FROM orders
        GROUP BY customer_id
        ORDER BY order_count DESC, customer_id ASC
        LIMIT ?
        """,
        (limit,)
    )


def get_missing_amount_count():
    """Count orders with missing amounts."""
    return execute_query(
        """
        SELECT COUNT(*)
        FROM orders
        WHERE order_amount IS NULL
        """
    )


def get_order_count_by_status(status):
    """Get the number of orders for a specific status."""
    return execute_query(
        """
        SELECT COUNT(*)
        FROM orders
        WHERE LOWER(status) = LOWER(?)
        """,
        (status,)
    )


if __name__ == "__main__":
    print("ORDER STATUS SUMMARY")

    result = get_order_summary()

    for row in result["rows"]:
        print(f"{row[0]}: {row[1]} orders")

    print("\nTOP 5 CUSTOMERS")

    result = get_top_customers(5)

    for row in result["rows"]:
        print(f"Customer {row[0]}: {row[1]} orders")

    print("\nMISSING ORDER AMOUNTS")

    result = get_missing_amount_count()
    print(f"Orders with missing amounts: {result['rows'][0][0]}")

    print("\nBUSINESS QUERY TEST COMPLETED!")