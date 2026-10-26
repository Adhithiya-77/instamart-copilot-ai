from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from backend.database import query_df, query_one
from backend.schemas import CustomerRecord

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=list[CustomerRecord])
def list_customers(
    search: Optional[str] = None,
    city: Optional[str] = None,
    sort_by: str = Query("order_count", pattern="^(order_count|recorded_spend|age|signup_date|customer_id)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(100, ge=1, le=500),
):
    where_clauses = []
    params: list = []

    if search:
        where_clauses.append("c.customer_id LIKE ?")
        params.append(f"%{search}%")
    if city:
        where_clauses.append("c.city = ?")
        params.append(city)

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    rows = query_df(
        f"""
        SELECT c.customer_id, c.city, c.age, c.gender, c.signup_date,
               COUNT(o.order_id) AS order_count,
               ROUND(SUM(o.order_amount), 2) AS recorded_spend
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        {where_sql}
        GROUP BY c.customer_id, c.city, c.age, c.gender, c.signup_date
        ORDER BY {sort_by} {sort_dir.upper()}
        LIMIT ?
        """,
        tuple(params) + (limit,),
    )
    return [CustomerRecord(**r) for r in rows]


@router.get("/cities")
def get_cities():
    rows = query_df("SELECT DISTINCT city FROM customers ORDER BY city")
    return [r["city"] for r in rows]


@router.get("/{customer_id}")
def get_customer(customer_id: str):
    customer = query_one(
        "SELECT * FROM customers WHERE customer_id = ?", (customer_id,)
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    orders = query_df("""
        SELECT o.order_id, p.product_name, o.order_ts,
               o.status, o.order_amount, o.delivery_minutes
        FROM orders o
        LEFT JOIN products p ON o.product_id = p.product_id
        WHERE o.customer_id = ?
        ORDER BY o.order_ts DESC LIMIT 20
    """, (customer_id,))
    return {"customer": customer, "recent_orders": orders}
