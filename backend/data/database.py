import os
import duckdb
from contextlib import contextmanager

# Absolute path to DuckDB file
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "qsr.duckdb")

class DatabaseManager:
    @staticmethod
    @contextmanager
    def get_connection():
        """
        Yields a read-only DuckDB connection and ensures it is closed after use.
        DuckDB allows concurrent read-only connections, which avoids locking issues.
        """
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"DuckDB database file not found at {DB_PATH}. Please run ingestion script first.")
        
        conn = duckdb.connect(DB_PATH, read_only=True)
        try:
            yield conn
        finally:
            conn.close()

    @staticmethod
    def execute_query(query: str, params=None):
        """
        Executes a query and returns results as list of dictionaries.
        """
        with DatabaseManager.get_connection() as conn:
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            
            # Fetch column names
            cols = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(cols, row)) for row in rows]

    @staticmethod
    def execute_query_df(query: str, params=None):
        """
        Executes a query and returns a pandas DataFrame.
        """
        with DatabaseManager.get_connection() as conn:
            if params:
                return conn.execute(query, params).fetchdf()
            else:
                return conn.execute(query).fetchdf()
