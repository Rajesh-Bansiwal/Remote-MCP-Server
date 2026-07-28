from fastmcp import FastMCP
import os 
import sqlite3
DB_PATH=os.path.join(os.path.dirname(__file__),"expenses.db")
CATEGORY_PATH=os.path.join(os.path.dirname(__file__),"categories.json")
mcp=FastMCP("ExpenseTracker")
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                note TEXT DEFAULT ''
            )
        """)
        
init_db()

@mcp.tool()
def add_expense(date,amount,category,subcategory="",note=""):
    """ADD NEW EXPENSE IN DATABASE"""
    with sqlite3.connect(DB_PATH) as c:
          curr= c.execute(
                """
                INSERT INTO expenses
                (date, amount, category, subcategory, note)
                VALUES (?, ?, ?, ?, ?)
                """,
                (date, amount, category, subcategory, note),
            )
          return {"status":"ok","id":curr.lastrowid}

@mcp.tool()
def list_expense():
    """LIST OF ALL TRANSACTIONS"""
    with sqlite3.connect(DB_PATH) as c:
        curr=c.execute("""
                SELECT
                    id,
                    date,
                    amount,
                    category,
                    subcategory,
                    note
                FROM expenses
                WHERE date BETWEEN ? AND ?
                ORDER id ASD
            """)
        cols=[d[0] for d in curr.description]
        return [dict(zip(cols,r)) for r in curr.fetchall()]
    
@mcp.tool()
def summarize_expenses(
    start_date: str = None,
    end_date: str = None,
    category: str = None
) -> dict:
    """
    Summarize expenses with optional filters.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        category: Expense category

    Returns:
        Summary statistics.
    """

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = """
                SELECT
                    COUNT(*) AS total_transactions,
                    COALESCE(SUM(amount), 0) AS total_amount,
                    COALESCE(AVG(amount), 0) AS average_amount,
                    COALESCE(MAX(amount), 0) AS highest_expense,
                    COALESCE(MIN(amount), 0) AS lowest_expense
                FROM expenses
                WHERE 1=1
            """

            params = []

            if start_date:
                query += " AND date >= ?"
                params.append(start_date)

            if end_date:
                query += " AND date <= ?"
                params.append(end_date)

            if category:
                query += " AND category = ?"
                params.append(category)

            cursor.execute(query, params)

            summary = dict(cursor.fetchone())

            return {
                "success": True,
                "filters": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "category": category,
                },
                "summary": summary,
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }

@mcp.resource("expense://categories",mime_type="application/json")
def categories():
    with open(CATEGORY_PATH,"r",encoding="utf-8") as f:
        return f.read()

if __name__ =="__main__":
    mcp.run(transport="http",host="0.0.0.0",port=8000)