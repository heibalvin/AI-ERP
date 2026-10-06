import psycopg
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres import PostgresSaver
from src.config import POSTGRES_URI

def get_db_connection():
    """Returns a psycopg (v3) database connection."""
    return psycopg.connect(POSTGRES_URI, row_factory=dict_row)

def ensure_tables_exist():
    """Creates api.ai_tasks table if it doesn't exist."""
    query = """
    CREATE SCHEMA IF NOT EXISTS api;
    CREATE TABLE IF NOT EXISTS api.ai_tasks (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        status VARCHAR(50) DEFAULT 'pending',
        due_date TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            conn.commit()

def get_checkpointer():
    """Initializes and returns the LangGraph PostgresSaver checkpointer using a psycopg v3 connection."""
    ensure_tables_exist()
    
    # Pass a psycopg v3 connection object directly
    conn = get_db_connection()
    checkpointer = PostgresSaver(conn)
    checkpointer.setup()
    return checkpointer