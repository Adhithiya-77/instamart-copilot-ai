import sqlite3
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "outputs" / "instamart.db"


def run_query(cursor, title, query):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    cursor.execute(query)
    rows = cursor.fetchall()

    if not rows:
        print("No results found.")
        return

    for row in rows:
        print(row)


def main():
    if not DB_PATH.exists():
        print("Database not found:", DB_PATH)
        return

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # 1. Total records
    run_query(
        cursor,
        "DATABASE SUMMARY",
        """
        SELECT 'Customers', COUNT(*) FROM customers
        UNION ALL
        SELECT 'Products', COUNT(*) FROM products
        UNION ALL
        SELECT 'Orders', COUNT(*) FROM orders;
        """
    )

    # 2. Order status summary
    run_query(
        cursor,
        "ORDER STATUS SUMMARY",
        """
        SELECT status, COUNT(*) AS total_orders
        FROM orders
        GROUP BY status
        ORDER BY total_orders DESC;
        """
    )

    # 3. Total recorded revenue
    run_query(
        cursor,
        "TOTAL RECORDED REVENUE",
        """
        SELECT ROUND(SUM(order_amount), 2)
        FROM orders
        WHERE order_amount IS NOT NULL;
        """
    )

    # 4. Average recorded order amount
    run_query(
        cursor,
        "AVERAGE RECORDED ORDER AMOUNT",
        """
        SELECT ROUND(AVG(order_amount), 2)
        FROM orders
        WHERE order_amount IS NOT NULL;
        """
    )

    # 5. Top 10 products by recorded revenue
    run_query(
        cursor,
        "TOP 10 PRODUCTS BY RECORDED REVENUE",
        """
        SELECT
            p.product_name,
            ROUND(SUM(o.order_amount), 2) AS revenue
        FROM orders o
        JOIN products p
            ON o.product_id = p.product_id
        WHERE o.order_amount IS NOT NULL
        GROUP BY p.product_id, p.product_name
        ORDER BY revenue DESC
        LIMIT 10;
        """
    )

    # 6. Top 10 customers by number of orders
    run_query(
        cursor,
        "TOP 10 CUSTOMERS BY ORDER COUNT",
        """
        SELECT
            customer_id,
            COUNT(*) AS total_orders
        FROM orders
        GROUP BY customer_id
        ORDER BY total_orders DESC
        LIMIT 10;
        """
    )

    # 7. Orders with missing amounts
    run_query(
        cursor,
        "ORDERS WITH MISSING AMOUNTS",
        """
        SELECT COUNT(*)
        FROM orders
        WHERE order_amount IS NULL;
        """
    )

    # 8. Orders with missing delivery times
    run_query(
        cursor,
        "ORDERS WITH MISSING DELIVERY TIMES",
        """
        SELECT COUNT(*)
        FROM orders
        WHERE delivery_minutes IS NULL;
        """
    )

    connection.close()

    print("\n" + "=" * 60)
    print("SQL ANALYTICS COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()