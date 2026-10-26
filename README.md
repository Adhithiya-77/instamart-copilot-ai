<<<<<<< HEAD
# Instamart Copilot

A business analytics dashboard for a fictional quick-commerce grocery platform.
Built with Python, Pandas, SQLite, and Streamlit. No paid API required.

---

## Features

| Section | What it does |
|---|---|
| **Overview** | Key metrics, order-status distribution, monthly volume trend, top products by revenue |
| **Orders** | Filterable and searchable order table, CSV export |
| **Products** | Catalogue, category breakdown, price ranges, top sellers by count |
| **Customers** | City and gender distribution, top customers by order count and spend |
| **Analytics** | Tabbed deep-dives: category revenue, product insights, customer insights, delivery times |
| **Business Assistant** | Natural-language questions answered via predefined SQL — no API key needed |
| **Data Quality** | Missing values, duplicate order IDs, referential integrity checks |

---

## Technology Stack

- **Python 3.10+**
- **Pandas** — data loading and transformation
- **SQLite** — embedded relational database (`outputs/instamart.db`)
- **Streamlit** — interactive web dashboard
- **SQL** — all analytics queries use parameterised, read-only SQL

---

## Project Structure

```
instamart-copilot/
├── app.py                  # Streamlit dashboard (main entry point)
├── requirements.txt        # Python dependencies
├── generate_data.py        # Synthetic data generator (run once)
├── mock_llm.py             # Offline LLM stub used in agent experiments
├── data/
│   ├── clean/              # Cleaned CSVs (customers, products, orders)
│   ├── raw/                # Raw source CSVs
│   └── policies/           # Policy text files
├── outputs/
│   └── instamart.db        # SQLite database
├── src/
│   ├── create_database.py  # Builds the SQLite DB from clean CSVs
│   ├── business_analytics.py
│   ├── sql_analytics.py
│   ├── business_query.py   # Reusable parameterised query functions
│   ├── validate_database.py
│   └── ...                 # Other analysis and audit scripts
└── .gitignore
```

---

## Setup (Windows PowerShell)

### 1. Clone the repository

```powershell
git clone https://github.com/<your-username>/instamart-copilot.git
cd instamart-copilot
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Verify the database exists

The file `outputs/instamart.db` should already be present.
If it is missing, rebuild it from the clean CSVs:

```powershell
python src/create_database.py
```

### 5. Run the dashboard

```powershell
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Business Assistant

The assistant maps natural-language questions to predefined, read-only SQL queries.
It does **not** use OpenAI or any paid API.

Supported question topics:
- Total order count
- Order status breakdown (completed / cancelled / pending)
- Recorded revenue and missing amounts
- Top products by order count
- Top customers by order count and spend
- City with the most customers
- Average delivery time
- Category revenue

Unsupported questions receive a clear message listing what is supported.

---

## Dataset

The dataset is **synthetic** — generated programmatically to simulate a
quick-commerce grocery platform operating across Indian cities.

| Table | Rows | Key columns |
|---|---|---|
| customers | 1,200 | customer_id, city, age, gender, signup_date |
| products | 40 | product_id, product_name, category, price_inr |
| orders | 12,965 | order_id, customer_id, product_id, status, order_amount, delivery_minutes, order_ts |

**Known data characteristics:**
- 118 orders have no recorded `order_amount` (~0.9%)
- 2,629 orders have no recorded `delivery_minutes` (~20%)
- 656 `order_id` values appear more than once (all correspond to pending orders)
- All customer and product foreign keys are valid (no orphan references)
- Date range: April 2025 – September 2025

---

## Known Limitations

- The Business Assistant uses keyword matching, not semantic understanding.
  Complex or ambiguous questions may not be routed correctly.
- Revenue figures are recorded amounts only; they do not represent
  recognised accounting revenue.
- The dataset is synthetic and does not reflect real business data.
- No authentication or multi-user support.

---

## Future Improvements

- Add Plotly charts for richer interactivity (hover tooltips, drill-down)
- Expand the assistant with more query patterns
- Add a date-range filter across all pages
- Export analytics summaries to PDF
- Add unit tests for the query functions in `src/business_query.py`

---

## Screenshots

_Add screenshots after running the application locally._

---

## License

MIT
=======
# instamart-copilot-ai
>>>>>>> 7aba9ea4a43ecbe6fd3fc0311ab195e375f3f89b
