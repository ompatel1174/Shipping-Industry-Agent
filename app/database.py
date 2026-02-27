import psycopg2
from app.config import settings


def get_connection():
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            port=settings.DB_PORT
        )
        return conn
    except Exception as e:
        print("Database connection error:", e)
        raise