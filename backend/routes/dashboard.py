from fastapi import APIRouter
from backend.database import query_df, query_one
from backend.schemas import (
    DashboardSummary, StatusCount, MonthlyTrend,
    TopProduct, CityCount, CategoryRevenue
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary():
    row = query_one("""
        SELECT
            COUNT(*) AS total_orders,
            SUM(CASE WHEN LOWER(status)='completed' THEN 1 ELSE 0 END) AS completed,
            SUM(CASE WHEN LOWER(status)='cancelled' THEN 1 ELSE 0 END) AS cancelled,
            SUM(CASE WHEN LOWER(status)='pending'   THEN 1 ELSE 0 END) AS pending,
            ROUND(SUM(CASE WHEN order_amount IS NOT NULL THEN order_amount ELSE 0 END),2) AS recorded_revenue,
            SUM(CASE WHEN order_amount IS NULL THEN 1 ELSE 0 END) AS missing_amounts,
            SUM(CASE WHEN delivery_minutes IS NULL THEN 1 ELSE 0 END) AS missing_delivery
        FROM orders
    """)
    customers = query_one("SELECT COUNT(*) AS n FROM customers")
    products  = query_one("SELECT COUNT(*) AS n FROM products")
    return DashboardSummary(
        total_orders=row["total_orders"],
        completed=row["completed"],
        cancelled=row["cancelled"],
        pending=row["pending"],
        recorded_revenue=row["recorded_revenue"] or 0.0,
        missing_amounts=row["missing_amounts"],
        missing_delivery=row["missing_delivery"],
        total_customers=customers["n"],
        total_products=products["n"],
    )


@router.get("/order-status", response_model=list[StatusCount])
def get_order_status():
    total = query_one("SELECT COUNT(*) AS n FROM orders")["n"]
    rows = query_df("SELECT status, COUNT(*) AS cnt FROM orders GROUP BY status ORDER BY cnt DESC")
    return [
        StatusCount(
            status=r["status"],
            count=r["cnt"],
            percentage=round(r["cnt"] / total * 100, 1) if total else 0.0,
        )
        for r in rows
    ]


@router.get("/order-trends", response_model=list[MonthlyTrend])
def get_order_trends():
    rows = query_df("""
        SELECT strftime('%Y-%m', order_ts) AS month, COUNT(*) AS orders
        FROM orders
        WHERE order_ts IS NOT NULL
        GROUP BY month ORDER BY month
    """)
    return [MonthlyTrend(month=r["month"], orders=r["orders"]) for r in rows]


@router.get("/top-products", response_model=list[TopProduct])
def get_top_products(limit: int = 10):
    rows = query_df("""
        SELECT p.product_name, p.category,
               COUNT(*) AS order_count,
               ROUND(SUM(o.order_amount),2) AS recorded_revenue
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY order_count DESC
        LIMIT ?
    """, (limit,))
    return [TopProduct(**r) for r in rows]


@router.get("/city-distribution", response_model=list[CityCount])
def get_city_distribution():
    rows = query_df("""
        SELECT city, COUNT(*) AS customers
        FROM customers GROUP BY city ORDER BY customers DESC
    """)
    return [CityCount(**r) for r in rows]


@router.get("/category-revenue", response_model=list[CategoryRevenue])
def get_category_revenue():
    rows = query_df("""
        SELECT p.category,
               COUNT(*) AS orders,
               ROUND(SUM(o.order_amount),2) AS recorded_revenue,
               ROUND(AVG(o.order_amount),2) AS avg_order
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE o.order_amount IS NOT NULL
        GROUP BY p.category ORDER BY recorded_revenue DESC
    """)
    return [CategoryRevenue(**r) for r in rows]


@router.get("/recent-orders")
def get_recent_orders(limit: int = 10):
    rows = query_df("""
        SELECT o.order_id, o.customer_id, p.product_name,
               o.order_ts, o.status, o.order_amount, o.delivery_minutes
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        ORDER BY o.order_ts DESC LIMIT ?
    """, (limit,))
    return rows
