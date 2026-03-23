# import psycopg2
# from psycopg2.extras import RealDictCursor
# from app.config import settings


# class SQLExecutionTool:

#     def __init__(self):
#         self.connection = psycopg2.connect(
#             host=settings.DB_HOST,
#             port=settings.DB_PORT,
#             database=settings.DB_NAME,
#             user=settings.DB_USER,
#             password=settings.DB_PASSWORD
#         )

#     def validate_query(self, query: str) -> bool:
#         query = query.strip().lower()

#         forbidden_keywords = [
#             "delete",
#             "update",
#             "insert",
#             "drop",
#             "truncate",
#             "alter",
#             "create"
#         ]

#         if not query.startswith("select"):
#             return False

#         for keyword in forbidden_keywords:
#             if keyword in query:
#                 return False

#         return True


#     def execute_query(self, query: str):

#         if not self.validate_query(query):
#             return {
#                 "success": False,
#                 "error": "Only SELECT queries are allowed",
#                 "data": None
#             }

#         try:
#             cursor = self.connection.cursor(cursor_factory=RealDictCursor)

#             cursor.execute(query)

#             results = cursor.fetchall()

#             cursor.close()

#             return {
#                 "success": True,
#                 "error": None,
#                 "data": results
#             }

#         except Exception as e:
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "data": None
#             }

#     def close(self):
#         if self.connection:
#             self.connection.close()

"""
Tool 2 – SQL Query Execution Tool

Executes SELECT queries against the PostgreSQL database.
Includes safety checks to prevent destructive operations.
"""

import re
from app.database import get_connection

# Patterns that are NOT allowed in user-generated queries
_BLOCKED_PATTERNS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)

MAX_ROWS = 500


def execute(sql: str) -> dict:
    """
    Execute a SQL SELECT query and return structured results.

    Args:
        sql: A SQL SELECT statement.

    Returns:
        dict with keys:
            - success: bool
            - columns: list of column names
            - rows: list of dicts (column -> value)
            - row_count: number of rows returned
            - error: error message if failed
            - sql: the executed SQL (for transparency)
    """
    # --- Safety check ---
    if _BLOCKED_PATTERNS.search(sql):
        return {
            "success": False,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "error": "Blocked: Only SELECT queries are allowed. Destructive statements are not permitted.",
            "sql": sql,
        }

    # Strip trailing semicolons and whitespace
    sql = sql.strip().rstrip(";")

    # Enforce row limit
    if "LIMIT" not in sql.upper():
        sql += f" LIMIT {MAX_ROWS}"

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)

        columns = [desc[0] for desc in cursor.description]
        raw_rows = cursor.fetchall()

        rows = [dict(zip(columns, row)) for row in raw_rows]

        return {
            "success": True,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "error": None,
            "sql": sql,
        }

    except Exception as e:
        return {
            "success": False,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "error": str(e),
            "sql": sql,
        }

    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
