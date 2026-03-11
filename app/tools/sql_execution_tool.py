import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import settings


class SQLExecutionTool:

    def __init__(self):
        self.connection = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )

    def validate_query(self, query: str) -> bool:
        """
        Only allow SELECT queries
        """
        query = query.strip().lower()

        forbidden_keywords = [
            "delete",
            "update",
            "insert",
            "drop",
            "truncate",
            "alter",
            "create"
        ]

        if not query.startswith("select"):
            return False

        for keyword in forbidden_keywords:
            if keyword in query:
                return False

        return True


    def execute_query(self, query: str):
        """
        Execute SQL query and return results
        """

        if not self.validate_query(query):
            return {
                "success": False,
                "error": "Only SELECT queries are allowed",
                "data": None
            }

        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)

            cursor.execute(query)

            results = cursor.fetchall()

            cursor.close()

            return {
                "success": True,
                "error": None,
                "data": results
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

    def close(self):
        if self.connection:
            self.connection.close()