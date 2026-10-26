import sqlite3
from pathlib import Path

# Database location
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "outputs" / "instamart.db"


def execute_sql(query, params=()):
    """
    Execute a read-only SQL query and return the results.
    Only SELECT queries are allowed.
    """

    if not isinstance(query, str):
        raise ValueError("Query must be a string.")

    query = query.strip()

    if not query:
        raise ValueError("Query cannot be empty.")

    # Allow only SELECT queries
    if not query.upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")

    connection = sqlite3.connect(DB_PATH)

    try:
        # Enable read-only query mode
        connection.execute("PRAGMA query_only = ON")

        cursor = connection.cursor()
        cursor.execute(query, params)

        columns = [
            description[0]
            for description in cursor.description
        ]

        rows = cursor.fetchall()

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows)
        }

    finally:
        connection.close()


if __name__ == "__main__":

    query = """
        SELECT status, COUNT(*) AS total_orders
        FROM orders
        GROUP BY status
        ORDER BY total_orders DESC
    """

    result = execute_sql(query)

    print("\nSQL QUERY RESULTS")
    print("=" * 50)

    print("Columns:", result["columns"])

    for row in result["rows"]:
        print(row)

    print("\nTotal result rows:", result["row_count"])
    print("SQL tool executed successfully!")