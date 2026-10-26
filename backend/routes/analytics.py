from fastapi import APIRouter
from backend.database import query_df, query_one

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/products")
def product_analytics():
    by_count = query_df("""
        SELECT p.product_name, p.category, COUNT(*) AS orders,
               COALESCE(SUM(o.quantity),0) AS qty_sold,
               ROUND(SUM(o.order_amount),2) AS recorded_revenue
        FROM orders o JOIN products p ON o.product_id=p.product_id
        GROUP BY p.product_id ORDER BY orders DESC LIMIT 20
    """)
    by_revenue = query_df("""
        SELECT p.product_name, p.category,
               ROUND(SUM(o.order_amount),2) AS recorded_revenue
        FROM orders o JOIN products p ON o.product_id=p.product_id
        WHERE o.order_amount IS NOT NULL
        GROUP BY p.product_id ORDER BY recorded_revenue DESC LIMIT 20
    """)
    return {"by_order_count": by_count, "by_revenue": by_revenue}


@router.get("/customers")
def customer_analytics():
    top_by_orders = query_df("""
        SELECT o.customer_id, c.city, c.gender,
               COUNT(*) AS orders,
               ROUND(SUM(o.order_amount),2) AS recorded_spend
        FROM orders o JOIN customers c ON o.customer_id=c.customer_id
        GROUP BY o.customer_id ORDER BY orders DESC LIMIT 15
    """)
    by_gender = query_df("""
        SELECT gender, COUNT(*) AS customers
        FROM customers GROUP BY gender ORDER BY customers DESC
    """)
    age_buckets = query_df("""
        SELECT
            CASE
                WHEN age < 25 THEN 'Under 25'
                WHEN age < 35 THEN '25-34'
                WHEN age < 45 THEN '35-44'
                WHEN age < 55 THEN '45-54'
                ELSE '55+'
            END AS age_group,
            COUNT(*) AS customers
        FROM customers
        GROUP BY age_group ORDER BY age_group
    """)
    return {
        "top_by_orders": top_by_orders,
        "by_gender": by_gender,
        "age_buckets": age_buckets,
    }


@router.get("/cities")
def city_analytics():
    rows = query_df("""
        SELECT c.city,
               COUNT(DISTINCT c.customer_id) AS customers,
               COUNT(o.order_id) AS orders,
               ROUND(SUM(o.order_amount),2) AS recorded_revenue
        FROM customers c
        LEFT JOIN orders o ON c.customer_id=o.customer_id
        GROUP BY c.city ORDER BY customers DESC
    """)
    return rows


@router.get("/delivery")
def delivery_analytics():
    summary = query_one("""
        SELECT ROUND(AVG(delivery_minutes),1) AS avg_minutes,
               ROUND(MIN(delivery_minutes),1) AS min_minutes,
               ROUND(MAX(delivery_minutes),1) AS max_minutes,
               COUNT(*) AS orders_with_data
        FROM orders WHERE delivery_minutes IS NOT NULL
    """)
    by_status = query_df("""
        SELECT status,
               ROUND(AVG(delivery_minutes),1) AS avg_minutes,
               COUNT(*) AS orders
        FROM orders WHERE delivery_minutes IS NOT NULL
        GROUP BY status
    """)
    return {"summary": summary, "by_status": by_status}
