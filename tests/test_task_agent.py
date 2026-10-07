#!/usr/bin/env python
"""
Test script for AI-Task-Agent CRUD operations.
Tests both the raw CRUD functions and the LangGraph agent with tools.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.task.crud import (
    create_task,
    get_task,
    list_tasks,
    list_tasks_by_date_range,
    update_task_status,
    delete_task,
)
from src.task.tools import (
    create_task_tool,
    get_tasks_tool,
    update_task_status_tool,
    delete_task_tool,
)
from src.task.agent import build_task_agent
from datetime import datetime, timedelta


def test_crud_functions():
    """Test raw CRUD functions directly."""
    print("=" * 50)
    print("Testing CRUD Functions")
    print("=" * 50)
    
    # Clean up any existing test tasks
    print("\n[SETUP] Cleaning up existing test tasks...")
    tasks = list_tasks()
    for t in tasks:
        if t['title'].startswith('[TEST]'):
            delete_task(t['id'])
    
    # Test CREATE
    print("\n[CREATE] Creating test task...")
    due = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    task = create_task(
        title="[TEST] Sample Task",
        description="Test description",
        due_date=due
    )
    assert task['id'] is not None
    assert task['title'] == "[TEST] Sample Task"
    assert task['status'] == "pending"
    print(f"  Created task ID: {task['id']}")
    task_id = task['id']
    
    # Test GET
    print("\n[READ] Getting task by ID...")
    retrieved = get_task(task_id)
    assert retrieved is not None
    assert retrieved['title'] == "[TEST] Sample Task"
    print(f"  Retrieved: {retrieved['title']}")
    
    # Test LIST (all)
    print("\n[READ] Listing all tasks...")
    all_tasks = list_tasks()
    assert any(t['id'] == task_id for t in all_tasks)
    print(f"  Found {len(all_tasks)} total tasks")
    
    # Test LIST by status
    print("\n[READ] Listing pending tasks...")
    pending = list_tasks(status="pending")
    assert any(t['id'] == task_id for t in pending)
    print(f"  Found {len(pending)} pending tasks")
    
    # Test LIST by date range
    print("\n[READ] Listing tasks by date range...")
    start = datetime.now().strftime("%Y-%m-%d 00:00:00")
    end = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d 23:59:59")
    range_tasks = list_tasks_by_date_range(start, end)
    assert any(t['id'] == task_id for t in range_tasks)
    print(f"  Found {len(range_tasks)} tasks in range")
    
    # Test UPDATE
    print("\n[UPDATE] Updating task status to 'completed'...")
    updated = update_task_status(task_id, "completed")
    assert updated['status'] == "completed"
    print(f"  Updated status: {updated['status']}")
    
    # Verify update
    verified = get_task(task_id)
    assert verified['status'] == "completed"
    print(f"  Verified status: {verified['status']}")
    
    # Test DELETE
    print("\n[DELETE] Deleting task...")
    deleted = delete_task(task_id)
    assert deleted is True
    print(f"  Deleted: {deleted}")
    
    # Verify deletion
    verified = get_task(task_id)
    assert verified is None
    print(f"  Verified deletion: {verified is None}")
    
    print("\n✓ All CRUD function tests passed!")


def test_tools():
    """Test LangChain tools."""
    print("\n" + "=" * 50)
    print("Testing LangChain Tools")
    print("=" * 50)
    
    # Clean up
    print("\n[SETUP] Cleaning up existing test tasks...")
    tasks = list_tasks()
    for t in tasks:
        if t['title'].startswith('[TEST-TOOL]'):
            delete_task(t['id'])
    
    # Test create_task_tool
    print("\n[TOOL] create_task_tool...")
    due = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    result = create_task_tool.invoke({
        "title": "[TEST-TOOL] Tool Task",
        "description": "Created via tool",
        "due_date": due
    })
    assert isinstance(result, dict)
    assert 'id' in result
    print(f"  Created task ID: {result['id']}")
    task_id = result['id']
    
    # Test get_tasks_tool (by status)
    print("\n[TOOL] get_tasks_tool (status=pending)...")
    result = get_tasks_tool.invoke({"status": "pending"})
    assert isinstance(result, list)
    assert any(t['id'] == task_id for t in result)
    print(f"  Found {len(result)} pending tasks")
    
    # Test get_tasks_tool (by date range)
    print("\n[TOOL] get_tasks_tool (date range)...")
    start = datetime.now().strftime("%Y-%m-%d 00:00:00")
    end = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d 23:59:59")
    result = get_tasks_tool.invoke({"start_date": start, "end_date": end})
    assert isinstance(result, list)
    assert any(t['id'] == task_id for t in result)
    print(f"  Found {len(result)} tasks in range")
    
    # Test update_task_status_tool
    print("\n[TOOL] update_task_status_tool...")
    result = update_task_status_tool.invoke({
        "task_id": task_id,
        "status": "cancelled"
    })
    assert isinstance(result, dict)
    assert result['status'] == "cancelled"
    print(f"  Updated status: {result['status']}")
    
    # Test delete_task_tool
    print("\n[TOOL] delete_task_tool...")
    result = delete_task_tool.invoke({"task_id": task_id})
    assert isinstance(result, dict)
    assert result['deleted'] is True
    print(f"  Deleted: {result['deleted']}")
    
    # Verify deletion
    result = get_tasks_tool.invoke({"status": "cancelled"})
    assert not any(t['id'] == task_id for t in result)
    print(f"  Verified deletion")
    
    print("\n✓ All tool tests passed!")


def test_agent():
    """Test the full LangGraph agent."""
    print("\n" + "=" * 50)
    print("Testing AI-Task-Agent (LangGraph)")
    print("=" * 50)
    
    # Clean up
    print("\n[SETUP] Cleaning up existing test tasks...")
    tasks = list_tasks()
    for t in tasks:
        if t['title'].startswith('[TEST-AGENT]'):
            delete_task(t['id'])
    
    agent = build_task_agent()
    
    # Test create via agent
    print("\n[AGENT] Create task...")
    due = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    result = agent.invoke({
        "messages": [("user", f"Create a task titled '[TEST-AGENT] Agent Task' with description 'Created via agent' due {due}")]
    })
    response = result["messages"][-1].content
    print(f"  Response: {response}")
    
    # Get the created task ID
    all_tasks = list_tasks()
    test_task = next((t for t in all_tasks if t['title'] == '[TEST-AGENT] Agent Task'), None)
    assert test_task is not None
    task_id = test_task['id']
    print(f"  Created task ID: {task_id}")
    
    # Test list via agent
    print("\n[AGENT] List pending tasks...")
    result = agent.invoke({
        "messages": [("user", "List all pending tasks")]
    })
    response = result["messages"][-1].content
    print(f"  Response: {response[:200]}...")
    
    # Test update via agent
    print("\n[AGENT] Update task status...")
    result = agent.invoke({
        "messages": [("user", f"Update task {task_id} status to completed")]
    })
    response = result["messages"][-1].content
    print(f"  Response: {response}")
    
    # Verify
    verified = get_task(task_id)
    assert verified['status'] == "completed"
    print(f"  Verified status: {verified['status']}")
    
    # Test delete via agent
    print("\n[AGENT] Delete task...")
    result = agent.invoke({
        "messages": [("user", f"Delete task {task_id}")]
    })
    response = result["messages"][-1].content
    print(f"  Response: {response}")
    
    # Verify deletion
    verified = get_task(task_id)
    assert verified is None
    print(f"  Verified deletion")
    
    print("\n✓ All agent tests passed!")


def test_erp_delegation():
    """Test the ERP agent delegation to task agent."""
    print("\n" + "=" * 50)
    print("Testing ERP Agent Delegation")
    print("=" * 50)
    
    from src.erp.agent import delegate_to_task_agent
    
    # Clean up
    print("\n[SETUP] Cleaning up existing test tasks...")
    tasks = list_tasks()
    for t in tasks:
        if t['title'].startswith('[TEST-ERP]'):
            delete_task(t['id'])
    
    # Test create with explicit dates
    print("\n[ERP] Create task via delegate_to_task_agent...")
    due = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    result = delegate_to_task_agent.invoke({
        "request": f"Create task '[TEST-ERP] ERP Task' due {due}",
        "start_date": datetime.now().strftime("%Y-%m-%d 00:00:00"),
        "end_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d 23:59:59")
    })
    print(f"  Response: {result}")
    
    # Test list with period
    print("\n[ERP] List tasks for tomorrow via delegate_to_task_agent...")
    result = delegate_to_task_agent.invoke({
        "request": "List tasks for tomorrow",
        "period": "tomorrow"
    })
    print(f"  Response: {result[:200]}...")
    
    # Test list with status
    print("\n[ERP] List pending tasks via delegate_to_task_agent...")
    result = delegate_to_task_agent.invoke({
        "request": "List pending tasks",
        "status": "pending"
    })
    print(f"  Response: {result[:200]}...")
    
    print("\n✓ ERP delegation tests passed!")


if __name__ == "__main__":
    print("Starting AI-Task-Agent CRUD Tests\n")
    
    try:
        test_crud_functions()
        test_tools()
        test_agent()
        test_erp_delegation()
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)