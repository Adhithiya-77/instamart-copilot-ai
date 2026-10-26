from fastapi import APIRouter, Query
from typing import Optional
from backend.database import query_df
from backend.schemas import ProductRecord

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductRecord])
def list_products(
    search: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: str = Query("order_count", pattern="^(order_count|price_inr|recorded_revenue|product_name)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
):
    where_clauses = []
    params: list = []

    if search:
        where_clauses.append("p.product_name LIKE ?")
        params.append(f"%{search}%")
    if category:
        where_clauses.append("p.category = ?")
        params.append(category)

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    rows = query_df(
        f"""
        SELECT p.product_id, p.product_name, p.category, p.price_inr,
               COUNT(o.order_id) AS order_count,
               COALESCE(SUM(o.quantity), 0) AS quantity_sold,
               ROUND(SUM(o.order_amount), 2) AS recorded_revenue
        FROM products p
        LEFT JOIN orders o ON p.product_id = o.product_id
        {where_sql}
        GROUP BY p.product_id, p.product_name, p.category, p.price_inr
        ORDER BY {sort_by} {sort_dir.upper()}
        """,
        tuple(params),
    )
    return [ProductRecord(**r) for r in rows]


@router.get("/categories")
def get_categories():
    rows = query_df("SELECT DISTINCT category FROM products ORDER BY category")
    return [r["category"] for r in rows]
