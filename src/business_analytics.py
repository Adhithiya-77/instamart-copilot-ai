import sqlite3
from pathlib import Path

# Database path
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "outputs" / "instamart.db"


def execute_query(cursor, title, query):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    cursor.execute(query)

    for row in cursor.fetchall():
        print(row)


def main():
    if not DB_PATH.exists():
        print("Database not found:", DB_PATH)
        return

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # 1. Cancellation rate
    execute_query(
        cursor,
        "ORDER CANCELLATION RATE",
        """
        SELECT
            COUNT(*) AS total_orders,
            SUM(CASE WHEN LOWER(status) = 'cancelled'
                     THEN 1 ELSE 0 END) AS cancelled_orders,
            ROUND(
                100.0 * SUM(
                    CASE WHEN LOWER(status) = 'cancelled'
                         THEN 1 ELSE 0 END
                ) / NULLIF(COUNT(*), 0),
                2
            ) AS cancellation_percentage
        FROM orders;
        """
    )

    # 2. Average delivery time
    execute_query(
        cursor,
        "AVERAGE DELIVERY TIME",
        """
        SELECT
            ROUND(AVG(delivery_minutes), 2) AS average_delivery_minutes
        FROM orders
        WHERE delivery_minutes IS NOT NULL
          AND delivery_minutes >= 0;
        """
    )

    # 3. Top 5 products by recorded revenue
    execute_query(
        cursor,
        "TOP 5 PRODUCTS BY RECORDED REVENUE",
        """
        SELECT
            p.product_name,
            ROUND(SUM(o.order_amount), 2) AS recorded_revenue
        FROM orders o
        JOIN products p
            ON o.product_id = p.product_id
        WHERE o.order_amount IS NOT NULL
        GROUP BY p.product_id, p.product_name
        ORDER BY recorded_revenue DESC
        LIMIT 5;
        """
    )

    # 4. Top 5 customers by order count
    execute_query(
        cursor,
        "TOP 5 CUSTOMERS BY ORDER COUNT",
        """
        SELECT
            customer_id,
            COUNT(*) AS order_count
        FROM orders
        GROUP BY customer_id
        ORDER BY order_count DESC
        LIMIT 5;
        """
    )

    # 5. Order status distribution
    execute_query(
        cursor,
        "ORDER STATUS DISTRIBUTION",
        """
        SELECT
            status,
            COUNT(*) AS order_count,
            ROUND(
                100.0 * COUNT(*) /
                NULLIF((SELECT COUNT(*) FROM orders), 0),
                2
            ) AS percentage
        FROM orders
        GROUP BY status
        ORDER BY order_count DESC;
        """
    )

    connection.close()
    print("\nBUSINESS ANALYTICS COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()