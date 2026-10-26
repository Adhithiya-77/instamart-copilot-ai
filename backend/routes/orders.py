from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from backend.database import query_df, query_one
from backend.schemas import OrderRecord, OrdersResponse

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("", response_model=OrdersResponse)
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("order_ts", pattern="^(order_ts|order_amount|status|delivery_minutes)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    where_clauses = []
    params: list = []

    if status:
        where_clauses.append("LOWER(o.status) = LOWER(?)")
        params.append(status)
    if search:
        where_clauses.append("(o.order_id LIKE ? OR o.customer_id LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])
    if date_from:
        where_clauses.append("o.order_ts >= ?")
        params.append(date_from)
    if date_to:
        where_clauses.append("o.order_ts <= ?")
        params.append(date_to + " 23:59:59")

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    count_row = query_one(
        f"SELECT COUNT(*) AS n FROM orders o {where_sql}", tuple(params)
    )
    total = count_row["n"]
    total_pages = max(1, (total + page_size - 1) // page_size)
    offset = (page - 1) * page_size

    sort_col = f"o.{sort_by}"
    rows = query_df(
        f"""
        SELECT o.order_id, o.customer_id, o.product_id,
               p.product_name,
               o.quantity, o.order_ts, o.status,
               o.discount_pct, o.order_amount, o.delivery_minutes
        FROM orders o
        LEFT JOIN products p ON o.product_id = p.product_id
        {where_sql}
        ORDER BY {sort_col} {sort_dir.upper()}
        LIMIT ? OFFSET ?
        """,
        tuple(params) + (page_size, offset),
    )

    return OrdersResponse(
        data=[OrderRecord(**r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{order_id}")
def get_order(order_id: str):
    rows = query_df("""
        SELECT o.*, p.product_name, p.category, p.price_inr
        FROM orders o
        LEFT JOIN products p ON o.product_id = p.product_id
        WHERE o.order_id = ?
    """, (order_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Order not found")
    return rows
