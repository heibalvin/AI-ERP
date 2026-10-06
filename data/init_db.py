import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from src.config import (
    POSTGRES_HOST,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
)

# Admin credentials (used to create the database/user if they don't exist yet)
ADMIN_USER = "postgres"
ADMIN_PASSWORD = "postgres"


def create_database_and_user():
    """Connects as admin to create the dedicated database and user if missing."""
    print("Connecting to PostgreSQL as admin...")
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            user=ADMIN_USER,
            password=ADMIN_PASSWORD,
            dbname="postgres",
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Create user if not exists
        cur.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = %s;", (POSTGRES_USER,)
        )
        if not cur.fetchone():
            print(f"Creating user '{POSTGRES_USER}'...")
            cur.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s;").format(
                    sql.Identifier(POSTGRES_USER)
                ),
                [POSTGRES_PASSWORD],
            )

        # Create database if not exists
        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s;", (POSTGRES_DB,)
        )
        if not cur.fetchone():
            print(f"Creating database '{POSTGRES_DB}'...")
            cur.execute(
                sql.SQL("CREATE DATABASE {} OWNER {};").format(
                    sql.Identifier(POSTGRES_DB),
                    sql.Identifier(POSTGRES_USER),
                )
            )

        cur.close()
        conn.close()
        print("Admin setup complete.")
    except Exception as e:
        print(f"Admin creation skipped/failed: {e}")


def apply_schema():
    """Connects to the application database and creates schemas and tables."""
    print(f"Connecting to '{POSTGRES_DB}' as '{POSTGRES_USER}'...")
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
    )
    cur = conn.cursor()

    # Define schema & table setup
    setup_queries = """
    CREATE SCHEMA IF NOT EXISTS api AUTHORIZATION CURRENT_USER;

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
    cur.execute(setup_queries)
    conn.commit()
    cur.close()
    conn.close()
    print("Database schema successfully applied!")


if __name__ == "__main__":
    create_database_and_user()
    apply_schema()