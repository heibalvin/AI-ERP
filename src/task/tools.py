from datetime import datetime, timedelta
from typing import Optional
from langchain_core.tools import tool
from src.task import crud

@tool
def list_tasks_by_period_tool(period: str = "all") -> str:
    """
    Lists tasks formatted by time period.
    - 'tomorrow': Outputs lines formatted as 'HH:MM : task description'.
    - 'week': Groups by day name and outputs 'HH:MM : task description' under each day.
    - 'all' / 'pending': Standard list format.
    """
    now = datetime.now()
    
    if period == "tomorrow":
        tomorrow = now + timedelta(days=1)
        start_str = tomorrow.strftime("%Y-%m-%d 00:00:00")
        end_str = tomorrow.strftime("%Y-%m-%d 23:59:59")
        tasks = crud.list_tasks_by_date_range(start_str, end_str)
        
        if not tasks:
            return "No tasks scheduled for tomorrow."
            
        lines = []
        for t in tasks:
            due = t.get("due_date")
            time_str = due.strftime("%H:%M") if isinstance(due, datetime) else "All day"
            lines.append(f"{time_str} : {t['title']} - {t.get('description', '')}".strip(" -"))
        return "\n".join(lines)

    elif period == "week":
        # Calculate current week range (Monday to Sunday)
        start_of_week = now - timedelta(days=now.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        start_str = start_of_week.strftime("%Y-%m-%d 00:00:00")
        end_str = end_of_week.strftime("%Y-%m-%d 23:59:59")
        tasks = crud.list_tasks_by_date_range(start_str, end_str)
        
        if not tasks:
            return "No tasks scheduled for this week."
            
        grouped = {}
        for t in tasks:
            due = t.get("due_date")
            if isinstance(due, datetime):
                day_name = due.strftime("%A (%Y-%m-%d)")
                time_str = due.strftime("%H:%M")
            else:
                day_name = "Unscheduled"
                time_str = "All day"
                
            grouped.setdefault(day_name, []).append(f"{time_str}: {t['title']}")
            
        output = []
        for day, items in grouped.items():
            output.append(f"\n{day}")
            output.extend(items)
        return "\n".join(output)

    else:
        tasks = crud.list_tasks(status=None if period == "all" else period)
        if not tasks:
            return "No tasks found."
        return "\n".join([f"[{t['id']}] {t['title']} - Status: {t['status']} (Due: {t['due_date']})" for t in tasks])

@tool
def create_task_tool(title: str, description: str = "", due_date: str = None) -> str:
    """Create a new task in PostgreSQL database."""
    task = crud.create_task(title=title, description=description, due_date=due_date)
    return f"Task created successfully! ID: {task['id']}, Title: '{task['title']}'."

@tool
def list_tasks_tool(status: str = None) -> str:
    """List existing tasks, optionally filtered by status ('pending', 'completed')."""
    tasks = crud.list_tasks(status=status)
    if not tasks:
        return "No tasks found."
    return "\n".join([f"[{t['id']}] {t['title']} - Status: {t['status']} (Due: {t['due_date']})" for t in tasks])

@tool
def update_task_status_tool(task_id: int, status: str) -> str:
    """Update the status of a specific task by its ID."""
    updated = crud.update_task_status(task_id=task_id, status=status)
    if updated:
        return f"Task {task_id} status updated to '{status}'."
    return f"Task {task_id} not found."