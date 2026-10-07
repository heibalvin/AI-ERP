from typing import Optional, List, Dict, Any
from langchain_core.tools import tool
from src.task import crud

@tool
def create_task_tool(title: str, description: Optional[str] = None, due_date: Optional[str] = None) -> Dict[str, Any]:
    """Create a new task in PostgreSQL database. Returns the created task record."""
    return crud.create_task(title=title, description=description, due_date=due_date)

@tool
def get_tasks_tool(status: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Query tasks by status and/or date range. Returns list of task records."""
    if start_date and end_date:
        return crud.list_tasks_by_date_range(start_date, end_date)
    return crud.list_tasks(status=status)

@tool
def update_task_status_tool(task_id: int, status: str) -> Dict[str, Any]:
    """Update the status of a specific task by its ID. Returns updated task record."""
    result = crud.update_task_status(task_id=task_id, status=status)
    if not result:
        raise ValueError(f"Task {task_id} not found")
    return result

@tool
def delete_task_tool(task_id: int) -> Dict[str, Any]:
    """Delete a task by its ID. Returns confirmation with task ID."""
    deleted = crud.delete_task(task_id)
    if not deleted:
        raise ValueError(f"Task {task_id} not found")
    return {"task_id": task_id, "deleted": True}