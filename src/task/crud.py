# src/task/crud.py
from typing import Optional, List, Dict, Any
from src.db import get_db_connection

def list_tasks_by_date_range(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Retrieves tasks with due_dates between start_date and end_date."""
    query = """
        SELECT * FROM api.ai_tasks 
        WHERE due_date >= %s AND due_date <= %s 
        ORDER BY due_date ASC;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (start_date, end_date))
            results = cur.fetchall()
            return [dict(row) for row in results]

def create_task(title: str, description: Optional[str] = None, due_date: Optional[str] = None) -> Dict[str, Any]:
    query = """
        INSERT INTO api.ai_tasks (title, description, due_date)
        VALUES (%s, %s, %s)
        RETURNING id, title, description, status, due_date, created_at;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (title, description, due_date))
            result = cur.fetchone()
            conn.commit()
            return dict(result)

def get_task(task_id: int) -> Optional[Dict[str, Any]]:
    query = "SELECT * FROM api.ai_tasks WHERE id = %s;"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (task_id,))
            result = cur.fetchone()
            return dict(result) if result else None

def list_tasks(status: Optional[str] = None) -> List[Dict[str, Any]]:
    if status:
        query = "SELECT * FROM api.ai_tasks WHERE status = %s ORDER BY id DESC;"
        params = (status,)
    else:
        query = "SELECT * FROM api.ai_tasks ORDER BY id DESC;"
        params = ()
        
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            results = cur.fetchall()
            return [dict(row) for row in results]

def update_task_status(task_id: int, status: str) -> Optional[Dict[str, Any]]:
    query = """
        UPDATE api.ai_tasks
        SET status = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id, title, status, updated_at;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (status, task_id))
            result = cur.fetchone()
            conn.commit()
            return dict(result) if result else None

def delete_task(task_id: int) -> bool:
    query = "DELETE FROM api.ai_tasks WHERE id = %s;"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (task_id,))
            deleted = cur.rowcount > 0
            conn.commit()
            return deleted