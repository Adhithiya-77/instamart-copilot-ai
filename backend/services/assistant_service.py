from backend.database import query_df, query_one

SUPPORTED_TOPICS = (
    "order counts, order status breakdown, completed/cancelled/pending orders, "
    "recorded revenue, missing amounts, top products, top customers, "
    "city distribution, delivery times, category performance, recent orders"
)


def _fmt_inr(v):
    if v is None:
        return "N/A"
    return f"\u20b9{v:,.2f}"


def handle(message: str) -> dict:
    q = message.lower().strip()

    # ── total orders ────────────────────────────────────────────────────────
    if any(k in q for k in ["how many order", "total order", "number of order", "count of order"]):
        row = query_one("SELECT COUNT(*) AS n FROM orders")
        return {"answer": f"There are **{row['n']:,}** order records in the database.", "supported": True}

    # ── status breakdown ────────────────────────────────────────────────────
    if any(k in q for k in ["status breakdown", "status summary", "orders by status",
                              "order status", "status distribution", "breakdown"]):
        total = query_one("SELECT COUNT(*) AS n FROM orders")["n"]
        rows = query_df("SELECT status, COUNT(*) AS cnt FROM orders GROUP BY status ORDER BY cnt DESC")
        cols = ["Status", "Orders", "Percentage"]
        data = [[r["status"], r["cnt"], f"{r['cnt']/total*100:.1f}%"] for r in rows]
        return {"answer": "Here is the order status breakdown:", "columns": cols, "data": data, "supported": True}

    # ── completed ───────────────────────────────────────────────────────────
    if "complet" in q and "miss" not in q:
        row = query_one("SELECT COUNT(*) AS n FROM orders WHERE LOWER(status)='completed'")
        return {"answer": f"**{row['n']:,}** orders have status *completed*.", "supported": True}

    # ── cancelled ───────────────────────────────────────────────────────────
    if "cancel" in q:
        row = query_one("SELECT COUNT(*) AS n FROM orders WHERE LOWER(status)='cancelled'")
        return {"answer": f"**{row['n']:,}** orders have status *cancelled*.", "supported": True}

    # ── pending ─────────────────────────────────────────────────────────────
    if "pending" in q:
        row = query_one("SELECT COUNT(*) AS n FROM orders WHERE LOWER(status)='pending'")
        return {"answer": f"**{row['n']:,}** orders have status *pending*.", "supported": True}

    # ── missing amounts ─────────────────────────────────────────────────────
    if any(k in q for k in ["missing amount", "no amount", "null amount", "missing order amount"]):
        row = query_one("SELECT COUNT(*) AS n FROM orders WHERE order_amount IS NULL")
        total = query_one("SELECT COUNT(*) AS n FROM orders")["n"]
        pct = round(row["n"] / total * 100, 1)
        return {"answer": f"**{row['n']:,}** orders ({pct}%) have no recorded order amount.", "supported": True}

    # ── recorded revenue ────────────────────────────────────────────────────
    if any(k in q for k in ["recorded", "revenue", "total amount", "order value", "how much"]):
        row = query_one("SELECT ROUND(SUM(order_amount),2) AS rev, COUNT(*) AS n FROM orders WHERE order_amount IS NOT NULL")
        return {
            "answer": f"Total recorded order amount: **{_fmt_inr(row['rev'])}**  \nBased on {row['n']:,} orders with a recorded amount.",
            "supported": True,
        }

    # ── top products ────────────────────────────────────────────────────────
    if any(k in q for k in ["top product", "best product", "sell the most", "most popular", "which product", "highest order"]):
        rows = query_df("""
            SELECT p.product_name, p.category, COUNT(*) AS orders
            FROM orders o JOIN products p ON o.product_id=p.product_id
            GROUP BY p.product_name ORDER BY orders DESC LIMIT 10
        """)
        cols = ["Product", "Category", "Orders"]
        data = [[r["product_name"], r["category"], r["orders"]] for r in rows]
        return {"answer": "Top 10 products by order count:", "columns": cols, "data": data, "supported": True}

    # ── top customers ───────────────────────────────────────────────────────
    if any(k in q for k in ["top customer", "best customer", "most order", "who are the top"]):
        rows = query_df("""
            SELECT o.customer_id, c.city, COUNT(*) AS orders,
                   ROUND(SUM(o.order_amount),2) AS recorded_spend
            FROM orders o JOIN customers c ON o.customer_id=c.customer_id
            GROUP BY o.customer_id ORDER BY orders DESC LIMIT 5
        """)
        cols = ["Customer ID", "City", "Orders", "Recorded Spend (INR)"]
        data = [[r["customer_id"], r["city"], r["orders"], r["recorded_spend"]] for r in rows]
        return {"answer": "Top 5 customers by order count:", "columns": cols, "data": data, "supported": True}

    # ── city distribution ───────────────────────────────────────────────────
    if any(k in q for k in ["city", "which city", "most customer", "customer by city"]):
        rows = query_df("SELECT city, COUNT(*) AS customers FROM customers GROUP BY city ORDER BY customers DESC LIMIT 10")
        cols = ["City", "Customers"]
        data = [[r["city"], r["customers"]] for r in rows]
        return {"answer": "Customer distribution by city:", "columns": cols, "data": data, "supported": True}

    # ── delivery time ───────────────────────────────────────────────────────
    if any(k in q for k in ["delivery time", "average delivery", "how long", "delivery"]):
        row = query_one("""
            SELECT ROUND(AVG(delivery_minutes),1) AS avg_min,
                   ROUND(MIN(delivery_minutes),1) AS min_min,
                   ROUND(MAX(delivery_minutes),1) AS max_min,
                   COUNT(*) AS n
            FROM orders WHERE delivery_minutes IS NOT NULL
        """)
        return {
            "answer": (
                f"Average delivery time: **{row['avg_min']} minutes**  \n"
                f"Range: {row['min_min']} – {row['max_min']} minutes  \n"
                f"Based on {row['n']:,} orders with recorded delivery times."
            ),
            "supported": True,
        }

    # ── category performance ────────────────────────────────────────────────
    if any(k in q for k in ["category", "categories", "category revenue", "category performance"]):
        rows = query_df("""
            SELECT p.category, COUNT(*) AS orders,
                   ROUND(SUM(o.order_amount),2) AS recorded_revenue
            FROM orders o JOIN products p ON o.product_id=p.product_id
            WHERE o.order_amount IS NOT NULL
            GROUP BY p.category ORDER BY recorded_revenue DESC
        """)
        cols = ["Category", "Orders", "Recorded Revenue (INR)"]
        data = [[r["category"], r["orders"], r["recorded_revenue"]] for r in rows]
        return {"answer": "Revenue by product category:", "columns": cols, "data": data, "supported": True}

    # ── recent orders ───────────────────────────────────────────────────────
    if any(k in q for k in ["latest order", "recent order", "show order", "last order"]):
        rows = query_df("""
            SELECT o.order_id, o.customer_id, p.product_name,
                   o.order_ts, o.status, o.order_amount
            FROM orders o JOIN products p ON o.product_id=p.product_id
            ORDER BY o.order_ts DESC LIMIT 10
        """)
        cols = ["Order ID", "Customer", "Product", "Date", "Status", "Amount (INR)"]
        data = [[r["order_id"], r["customer_id"], r["product_name"],
                 r["order_ts"], r["status"], r["order_amount"]] for r in rows]
        return {"answer": "10 most recent orders:", "columns": cols, "data": data, "supported": True}

    # ── unsupported ─────────────────────────────────────────────────────────
    return {
        "answer": (
            f"I can answer questions about: {SUPPORTED_TOPICS}. "
            "Please try rephrasing your question using one of those topics."
        ),
        "supported": False,
    }
