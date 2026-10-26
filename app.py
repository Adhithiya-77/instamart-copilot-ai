import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "outputs" / "instamart.db"

st.set_page_config(
    page_title="Instamart Copilot",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Minimal CSS: clean BI palette, no gimmicks ──────────────────────────────
st.markdown("""
<style>
/* Base */
html, body, [data-testid="stAppViewContainer"] {
    background: #f8f9fa;
    color: #1a1a2e;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
}
/* Metric cards */
[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
[data-testid="stMetricValue"] { color: #1a1a2e; font-weight: 700; }
[data-testid="stMetricLabel"] { color: #64748b; font-size: 0.82rem; }
/* Buttons */
.stButton > button {
    background: #2d6a4f;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 8px 20px;
    font-weight: 600;
    font-size: 0.88rem;
}
.stButton > button:hover { background: #1b4332; }
/* Section headers */
h2 { color: #1a1a2e; font-weight: 700; margin-top: 1.4rem; }
h3 { color: #2d3748; font-weight: 600; }
/* Sidebar nav label */
[data-testid="stSidebar"] .stRadio label { font-size: 0.9rem; }
/* Divider */
hr { border-color: #e2e8f0; }
/* Caption / note */
.note {
    background: #f0fdf4;
    border-left: 3px solid #2d6a4f;
    padding: 8px 12px;
    border-radius: 0 4px 4px 0;
    font-size: 0.82rem;
    color: #374151;
    margin: 6px 0 14px 0;
}
</style>
""", unsafe_allow_html=True)


# ── Database helpers ─────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_data():
    if not DB_PATH.exists():
        st.error(f"Database not found: {DB_PATH}")
        st.stop()
    with sqlite3.connect(DB_PATH) as conn:
        customers = pd.read_sql_query("SELECT * FROM customers", conn)
        products  = pd.read_sql_query("SELECT * FROM products",  conn)
        orders    = pd.read_sql_query("SELECT * FROM orders",    conn)
    orders["order_amount"] = pd.to_numeric(orders["order_amount"], errors="coerce")
    orders["order_ts"]     = pd.to_datetime(orders["order_ts"],    errors="coerce")
    return customers, products, orders


def query(sql, params=()):
    """Run a read-only parameterised query; return DataFrame."""
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn, params=params)


customers, products, orders = load_data()


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### Instamart Copilot")
    st.caption("Business Analytics Dashboard")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["Overview", "Orders", "Products", "Customers",
         "Analytics", "Business Assistant", "Data Quality"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("Python · Pandas · SQLite · Streamlit")


# ── Shared computed values ────────────────────────────────────────────────────

total_orders     = len(orders)
completed        = (orders["status"].str.lower() == "completed").sum()
cancelled        = (orders["status"].str.lower() == "cancelled").sum()
pending          = (orders["status"].str.lower() == "pending").sum()
recorded_revenue = orders["order_amount"].sum()
missing_amounts  = orders["order_amount"].isna().sum()


# ════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ════════════════════════════════════════════════════════════════════════════

if page == "Overview":
    st.title("Instamart — Business Overview")
    st.caption("Key metrics derived from the SQLite database. Amounts are recorded values only.")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Orders",     f"{total_orders:,}")
    c2.metric("Completed",        f"{completed:,}")
    c3.metric("Cancelled",        f"{cancelled:,}")
    c4.metric("Pending",          f"{pending:,}")
    c5.metric("Recorded Revenue", f"₹{recorded_revenue:,.0f}")

    st.markdown('<p class="note">Revenue = sum of non-null order_amount values only. '
                f'{missing_amounts:,} orders have no recorded amount.</p>',
                unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Order Status Distribution")
        status_df = (
            orders["status"].value_counts()
            .rename_axis("Status").reset_index(name="Orders")
        )
        st.bar_chart(status_df.set_index("Status"))

    with col_b:
        st.subheader("Monthly Order Volume")
        monthly = (
            orders.dropna(subset=["order_ts"])
            .assign(month=lambda d: d["order_ts"].dt.to_period("M").astype(str))
            .groupby("month")["order_id"].count()
            .rename_axis("Month").rename("Orders")
        )
        st.line_chart(monthly)

    st.subheader("Top 10 Products by Recorded Revenue")
    top_rev = query("""
        SELECT p.product_name, ROUND(SUM(o.order_amount),2) AS revenue
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE o.order_amount IS NOT NULL
        GROUP BY p.product_name
        ORDER BY revenue DESC LIMIT 10
    """).set_index("product_name")
    st.bar_chart(top_rev)

    col_c, col_d = st.columns(2)
    with col_c:
        st.subheader("Customers")
        st.metric("Total Customers", f"{len(customers):,}")
    with col_d:
        st.subheader("Products")
        st.metric("Total Products", f"{len(products):,}")


# ════════════════════════════════════════════════════════════════════════════
# PAGE: ORDERS
# ════════════════════════════════════════════════════════════════════════════

elif page == "Orders":
    st.title("Orders Explorer")

    col1, col2 = st.columns([2, 3])
    with col1:
        status_opts = ["All"] + sorted(orders["status"].dropna().unique().tolist())
        sel_status = st.selectbox("Filter by status", status_opts)
    with col2:
        search_id = st.text_input("Search by Order ID or Customer ID", placeholder="e.g. ORD-001 or C0227")

    filtered = orders.copy()
    if sel_status != "All":
        filtered = filtered[filtered["status"] == sel_status]
    if search_id.strip():
        s = search_id.strip().upper()
        filtered = filtered[
            filtered["order_id"].astype(str).str.upper().str.contains(s, na=False) |
            filtered["customer_id"].astype(str).str.upper().str.contains(s, na=False)
        ]

    st.caption(f"Showing {len(filtered):,} of {total_orders:,} orders")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download as CSV", data=csv,
                       file_name="instamart_orders.csv", mime="text/csv")


# ════════════════════════════════════════════════════════════════════════════
# PAGE: PRODUCTS
# ════════════════════════════════════════════════════════════════════════════

elif page == "Products":
    st.title("Products")

    col1, col2 = st.columns(2)
    col1.metric("Total Products", f"{len(products):,}")
    col2.metric("Categories", f"{products['category'].nunique()}")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Products by Category")
        cat_counts = (
            products["category"].value_counts()
            .rename_axis("Category").rename("Products")
        )
        st.bar_chart(cat_counts)

    with col_b:
        st.subheader("Price Range by Category")
        price_summary = (
            products.groupby("category")["price_inr"]
            .agg(Min="min", Max="max", Avg="mean")
            .round(0).astype(int)
        )
        st.dataframe(price_summary, use_container_width=True)

    st.subheader("Top 10 Products by Order Count")
    top_count = query("""
        SELECT p.product_name, p.category, COUNT(*) AS orders
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY p.product_name, p.category
        ORDER BY orders DESC LIMIT 10
    """)
    st.dataframe(top_count, use_container_width=True, hide_index=True)

    st.subheader("Product Catalogue")
    cat_filter = st.selectbox("Filter by category",
                              ["All"] + sorted(products["category"].unique().tolist()))
    disp = products if cat_filter == "All" else products[products["category"] == cat_filter]
    st.dataframe(disp, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: CUSTOMERS
# ════════════════════════════════════════════════════════════════════════════

elif page == "Customers":
    st.title("Customers")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Customers", f"{len(customers):,}")
    c2.metric("Cities", f"{customers['city'].nunique()}")
    c3.metric("Avg Age", f"{customers['age'].mean():.0f} yrs")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Customers by City")
        city_df = (
            customers["city"].value_counts()
            .rename_axis("City").rename("Customers")
        )
        st.bar_chart(city_df)

    with col_b:
        st.subheader("Gender Distribution")
        gender_df = (
            customers["gender"].value_counts()
            .rename_axis("Gender").rename("Customers")
        )
        st.bar_chart(gender_df)

    st.subheader("Top 10 Customers by Order Count")
    top_cust = query("""
        SELECT o.customer_id, c.city, COUNT(*) AS orders,
               ROUND(SUM(o.order_amount),2) AS recorded_spend
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY o.customer_id
        ORDER BY orders DESC LIMIT 10
    """)
    st.dataframe(top_cust, use_container_width=True, hide_index=True)

    st.subheader("Customer Records")
    city_filter = st.selectbox("Filter by city",
                               ["All"] + sorted(customers["city"].unique().tolist()))
    disp_c = customers if city_filter == "All" else customers[customers["city"] == city_filter]
    st.dataframe(disp_c, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ════════════════════════════════════════════════════════════════════════════

elif page == "Analytics":
    st.title("Analytics")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Category Performance", "Product Insights", "Customer Insights", "Delivery"])

    with tab1:
        st.subheader("Revenue by Category")
        cat_rev = query("""
            SELECT p.category,
                   COUNT(*) AS orders,
                   ROUND(SUM(o.order_amount),2) AS recorded_revenue,
                   ROUND(AVG(o.order_amount),2) AS avg_order
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            WHERE o.order_amount IS NOT NULL
            GROUP BY p.category
            ORDER BY recorded_revenue DESC
        """)
        st.dataframe(cat_rev, use_container_width=True, hide_index=True)
        st.bar_chart(cat_rev.set_index("category")["recorded_revenue"])

    with tab2:
        st.subheader("Top 15 Products by Order Count")
        prod_cnt = query("""
            SELECT p.product_name, p.category, COUNT(*) AS orders
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            GROUP BY p.product_name, p.category
            ORDER BY orders DESC LIMIT 15
        """)
        st.dataframe(prod_cnt, use_container_width=True, hide_index=True)

        st.subheader("Top 15 Products by Recorded Revenue")
        prod_rev = query("""
            SELECT p.product_name, p.category,
                   ROUND(SUM(o.order_amount),2) AS revenue
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            WHERE o.order_amount IS NOT NULL
            GROUP BY p.product_name, p.category
            ORDER BY revenue DESC LIMIT 15
        """)
        st.dataframe(prod_rev, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Top 15 Customers by Order Count")
        cust_ord = query("""
            SELECT o.customer_id, c.city, c.age, c.gender,
                   COUNT(*) AS orders,
                   ROUND(SUM(o.order_amount),2) AS recorded_spend
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            GROUP BY o.customer_id
            ORDER BY orders DESC LIMIT 15
        """)
        st.dataframe(cust_ord, use_container_width=True, hide_index=True)

        st.subheader("Orders per City")
        city_orders = query("""
            SELECT c.city, COUNT(*) AS orders
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            GROUP BY c.city
            ORDER BY orders DESC
        """)
        st.bar_chart(city_orders.set_index("city"))

    with tab4:
        st.subheader("Delivery Time Distribution")
        del_df = orders.dropna(subset=["delivery_minutes"])
        if not del_df.empty:
            avg_del = del_df["delivery_minutes"].mean()
            med_del = del_df["delivery_minutes"].median()
            c1, c2, c3 = st.columns(3)
            c1.metric("Avg Delivery (min)", f"{avg_del:.1f}")
            c2.metric("Median Delivery (min)", f"{med_del:.1f}")
            c3.metric("Orders with Delivery Data",
                      f"{len(del_df):,} / {total_orders:,}")

            st.subheader("Avg Delivery Time by Status")
            del_status = query("""
                SELECT status,
                       ROUND(AVG(delivery_minutes),1) AS avg_minutes,
                       COUNT(*) AS orders
                FROM orders
                WHERE delivery_minutes IS NOT NULL
                GROUP BY status
            """)
            st.dataframe(del_status, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: BUSINESS ASSISTANT
# ════════════════════════════════════════════════════════════════════════════

elif page == "Business Assistant":
    st.title("Business Assistant")
    st.caption(
        "Ask a natural-language question about the Instamart database. "
        "Answers are generated from predefined SQL queries — no API key required."
    )

    EXAMPLES = [
        "How many orders are there?",
        "Show the order status breakdown",
        "How many orders were completed?",
        "How many orders were cancelled?",
        "How many orders are pending?",
        "Which products sell the most?",
        "Who are the top 5 customers?",
        "How much recorded order value is available?",
        "How many orders have missing amounts?",
        "Which city has the most customers?",
        "What is the average delivery time?",
        "Show category revenue",
    ]

    with st.expander("Example questions"):
        for ex in EXAMPLES:
            st.markdown(f"- {ex}")

    question = st.text_input("Your question", placeholder="e.g. How many completed orders?")

    if st.button("Get Answer"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            q = question.lower().strip()

            # ── Route to the right analytics function ──────────────────────

            if any(k in q for k in ["how many order", "total order", "number of order"]):
                st.success(f"There are **{total_orders:,}** orders in the database.")

            elif any(k in q for k in ["status breakdown", "status summary",
                                       "orders by status", "order status", "status distribution"]):
                df = query("""
                    SELECT status,
                           COUNT(*) AS orders,
                           ROUND(100.0*COUNT(*)/?, 1) AS pct
                    FROM orders GROUP BY status ORDER BY orders DESC
                """, (total_orders,))
                st.dataframe(df, use_container_width=True, hide_index=True)

            elif "complet" in q:
                st.success(f"**{completed:,}** orders have status *completed*.")

            elif "cancel" in q:
                st.success(f"**{cancelled:,}** orders have status *cancelled*.")

            elif "pending" in q:
                st.success(f"**{pending:,}** orders have status *pending*.")

            elif any(k in q for k in ["missing amount", "no amount", "null amount"]):
                st.success(
                    f"**{missing_amounts:,}** orders have no recorded order amount "
                    f"({100*missing_amounts/total_orders:.1f}% of all orders)."
                )

            elif any(k in q for k in ["recorded value", "total revenue", "total amount",
                                       "order value", "how much"]):
                st.success(
                    f"Total recorded order amount: **₹{recorded_revenue:,.2f}**  \n"
                    f"Based on {total_orders - missing_amounts:,} orders with a recorded amount."
                )

            elif any(k in q for k in ["top customer", "best customer", "most order"]):
                df = query("""
                    SELECT o.customer_id, c.city,
                           COUNT(*) AS orders,
                           ROUND(SUM(o.order_amount),2) AS recorded_spend
                    FROM orders o
                    JOIN customers c ON o.customer_id = c.customer_id
                    GROUP BY o.customer_id
                    ORDER BY orders DESC LIMIT 5
                """)
                st.subheader("Top 5 Customers by Order Count")
                st.dataframe(df, use_container_width=True, hide_index=True)

            elif any(k in q for k in ["top product", "best product", "sell the most",
                                       "most popular", "which product"]):
                df = query("""
                    SELECT p.product_name, p.category, COUNT(*) AS orders
                    FROM orders o
                    JOIN products p ON o.product_id = p.product_id
                    GROUP BY p.product_name
                    ORDER BY orders DESC LIMIT 10
                """)
                st.subheader("Top 10 Products by Order Count")
                st.dataframe(df, use_container_width=True, hide_index=True)

            elif any(k in q for k in ["city", "which city", "most customer"]):
                df = query("""
                    SELECT city, COUNT(*) AS customers
                    FROM customers
                    GROUP BY city ORDER BY customers DESC LIMIT 10
                """)
                st.subheader("Customers by City")
                st.dataframe(df, use_container_width=True, hide_index=True)

            elif any(k in q for k in ["delivery time", "average delivery", "how long"]):
                df = query("""
                    SELECT ROUND(AVG(delivery_minutes),1) AS avg_minutes,
                           ROUND(MIN(delivery_minutes),1) AS min_minutes,
                           ROUND(MAX(delivery_minutes),1) AS max_minutes,
                           COUNT(*) AS orders_with_data
                    FROM orders WHERE delivery_minutes IS NOT NULL
                """)
                st.subheader("Delivery Time Summary")
                st.dataframe(df, use_container_width=True, hide_index=True)

            elif any(k in q for k in ["category", "categories"]):
                df = query("""
                    SELECT p.category,
                           COUNT(*) AS orders,
                           ROUND(SUM(o.order_amount),2) AS recorded_revenue
                    FROM orders o
                    JOIN products p ON o.product_id = p.product_id
                    WHERE o.order_amount IS NOT NULL
                    GROUP BY p.category ORDER BY recorded_revenue DESC
                """)
                st.subheader("Revenue by Category")
                st.dataframe(df, use_container_width=True, hide_index=True)

            else:
                st.info(
                    "This assistant answers questions about: order counts, order status, "
                    "completed / cancelled / pending orders, recorded revenue, missing amounts, "
                    "top products, top customers, city distribution, delivery times, "
                    "and category performance."
                )


# ════════════════════════════════════════════════════════════════════════════
# PAGE: DATA QUALITY
# ════════════════════════════════════════════════════════════════════════════

elif page == "Data Quality":
    st.title("Data Quality Report")
    st.caption("Validation findings from the Instamart SQLite database.")

    # ── Summary metrics ──────────────────────────────────────────────────────
    missing_delivery = orders["delivery_minutes"].isna().sum()
    dup_order_ids = query("""
        SELECT COUNT(*) AS n FROM (
            SELECT order_id FROM orders
            GROUP BY order_id HAVING COUNT(*) > 1
        )
    """).iloc[0, 0]

    orphan_customers = query("""
        SELECT COUNT(*) AS n FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """).iloc[0, 0]

    orphan_products = query("""
        SELECT COUNT(*) AS n FROM orders o
        LEFT JOIN products p ON o.product_id = p.product_id
        WHERE p.product_id IS NULL
    """).iloc[0, 0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Missing order_amount",    f"{missing_amounts:,}")
    c2.metric("Missing delivery_minutes", f"{missing_delivery:,}")
    c3.metric("Order IDs with duplicates", f"{dup_order_ids:,}")
    c4.metric("Orphan FK references",    f"{orphan_customers + orphan_products:,}")

    st.markdown("---")

    st.subheader("Missing Values per Column (orders table)")
    missing_cols = orders.isnull().sum().reset_index()
    missing_cols.columns = ["Column", "Missing"]
    missing_cols["Pct"] = (missing_cols["Missing"] / len(orders) * 100).round(1)
    st.dataframe(missing_cols, use_container_width=True, hide_index=True)

    st.subheader("Duplicate Order IDs")
    st.markdown(
        f"**{dup_order_ids:,}** order_id values appear more than once. "
        "These correspond to the **pending** orders in the dataset — "
        "each pending order shares an ID with its originating record."
    )
    if dup_order_ids > 0:
        dup_sample = query("""
            SELECT order_id, COUNT(*) AS occurrences
            FROM orders
            GROUP BY order_id HAVING COUNT(*) > 1
            ORDER BY occurrences DESC LIMIT 10
        """)
        st.dataframe(dup_sample, use_container_width=True, hide_index=True)

    st.subheader("Referential Integrity")
    ri_data = {
        "Check": [
            "Orders → valid customer_id",
            "Orders → valid product_id",
        ],
        "Violations": [orphan_customers, orphan_products],
        "Result": [
            "Pass" if orphan_customers == 0 else "Fail",
            "Pass" if orphan_products == 0 else "Fail",
        ],
    }
    st.dataframe(pd.DataFrame(ri_data), use_container_width=True, hide_index=True)

    st.subheader("Completed Orders with Missing Amounts")
    completed_missing = query("""
        SELECT COUNT(*) AS n FROM orders
        WHERE LOWER(TRIM(status)) = 'completed'
          AND order_amount IS NULL
    """).iloc[0, 0]
    st.metric("Completed orders missing amount", f"{completed_missing:,}")

    st.subheader("Order Date Range")
    date_range = query("SELECT MIN(order_ts) AS earliest, MAX(order_ts) AS latest FROM orders")
    st.dataframe(date_range, use_container_width=True, hide_index=True)
