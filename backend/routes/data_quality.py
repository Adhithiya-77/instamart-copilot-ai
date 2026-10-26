from fastapi import APIRouter
from backend.database import query_df, query_one
from backend.schemas import DataQualitySummary

router = APIRouter(prefix="/api/data-quality", tags=["data-quality"])


@router.get("/summary", response_model=DataQualitySummary)
def get_summary():
    row = query_one("""
        SELECT
            COUNT(*) AS total_orders,
            SUM(CASE WHEN order_amount IS NULL THEN 1 ELSE 0 END) AS missing_amounts,
            SUM(CASE WHEN delivery_minutes IS NULL THEN 1 ELSE 0 END) AS missing_delivery
        FROM orders
    """)
    dup = query_one("""
        SELECT COUNT(*) AS n FROM (
            SELECT order_id FROM orders GROUP BY order_id HAVING COUNT(*) > 1
        )
    """)
    orphan_c = query_one("""
        SELECT COUNT(*) AS n FROM orders o
        LEFT JOIN customers c ON o.customer_id=c.customer_id
        WHERE c.customer_id IS NULL
    """)
    orphan_p = query_one("""
        SELECT COUNT(*) AS n FROM orders o
        LEFT JOIN products p ON o.product_id=p.product_id
        WHERE p.product_id IS NULL
    """)
    comp_missing = query_one("""
        SELECT COUNT(*) AS n FROM orders
        WHERE LOWER(TRIM(status))='completed' AND order_amount IS NULL
    """)
    total = row["total_orders"]
    return DataQualitySummary(
        total_orders=total,
        missing_amounts=row["missing_amounts"],
        missing_amounts_pct=round(row["missing_amounts"] / total * 100, 1) if total else 0,
        missing_delivery=row["missing_delivery"],
        missing_delivery_pct=round(row["missing_delivery"] / total * 100, 1) if total else 0,
        duplicate_order_ids=dup["n"],
        orphan_customer_refs=orphan_c["n"],
        orphan_product_refs=orphan_p["n"],
        completed_missing_amount=comp_missing["n"],
    )


@router.get("/duplicates")
def get_duplicates(limit: int = 20):
    rows = query_df("""
        SELECT order_id, COUNT(*) AS occurrences, GROUP_CONCAT(status) AS statuses
        FROM orders GROUP BY order_id HAVING COUNT(*) > 1
        ORDER BY occurrences DESC LIMIT ?
    """, (limit,))
    return rows


@router.get("/missing-amounts")
def get_missing_amounts(limit: int = 20):
    rows = query_df("""
        SELECT order_id, customer_id, product_id, order_ts, status
        FROM orders WHERE order_amount IS NULL
        ORDER BY order_ts DESC LIMIT ?
    """, (limit,))
    return rows


@router.get("/column-nulls")
def get_column_nulls():
    row = query_one("""
        SELECT
            SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS order_id,
            SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS customer_id,
            SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) AS product_id,
            SUM(CASE WHEN quantity IS NULL THEN 1 ELSE 0 END) AS quantity,
            SUM(CASE WHEN order_ts IS NULL THEN 1 ELSE 0 END) AS order_ts,
            SUM(CASE WHEN status IS NULL THEN 1 ELSE 0 END) AS status,
            SUM(CASE WHEN order_amount IS NULL THEN 1 ELSE 0 END) AS order_amount,
            SUM(CASE WHEN delivery_minutes IS NULL THEN 1 ELSE 0 END) AS delivery_minutes,
            COUNT(*) AS total
        FROM orders
    """)
    total = row.pop("total")
    return [
        {"column": col, "missing": val, "pct": round(val / total * 100, 1)}
        for col, val in row.items()
    ]
