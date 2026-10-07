# AI-Task-Agent

Sub-agent for task CRUD operations against PostgreSQL (`api.ai_tasks` table).

## Architecture

- **AI-Task-Agent** (`src/task/agent.py`): LangGraph agent with 4 database tools
- **Tools** (`src/task/tools.py`): Raw CRUD tools returning structured data
- **CRUD** (`src/task/crud.py`): Direct PostgreSQL operations

## Quick Start

### 1. Prerequisites

```bash
# PostgreSQL running with database 'ai-erp-database'
# Ollama running with llama3.1:8b model
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
# Creates database, schema, and ai_tasks table (run from project root)
python -m data.init_db
```

### 4. Run Tests

```bash
# Test all CRUD layers (functions, tools, agent, ERP delegation)
python -m tests.test_task_agent
```

### 5. Run Interactive Agent

```bash
# Start the full AI-ERP agent (includes task delegation)
python -m src.main
```

## Tool Interface

| Tool | Parameters | Returns |
|------|------------|---------|
| `create_task_tool` | `title`, `description?`, `due_date?` | `Dict` (task record) |
| `get_tasks_tool` | `status?`, `start_date?`, `end_date?` | `List[Dict]` |
| `update_task_status_tool` | `task_id`, `status` | `Dict` (updated task) |
| `delete_task_tool` | `task_id` | `Dict` (`{"task_id": int, "deleted": bool}`) |

## Example Usage

### Direct Tool Calls

```python
from src.task.tools import create_task_tool, get_tasks_tool

# Create
task = create_task_tool.invoke({
    "title": "Finish report",
    "description": "Q4 financial report",
    "due_date": "2026-10-10 17:00:00"
})

# Query
tasks = get_tasks_tool.invoke({"status": "pending"})
tasks = get_tasks_tool.invoke({
    "start_date": "2026-10-06 00:00:00",
    "end_date": "2026-10-06 23:59:59"
})
```

### Via AI-Task-Agent

```python
from src.task.agent import build_task_agent

agent = build_task_agent()
result = agent.invoke({
    "messages": [("user", "Create task 'Review PR' due tomorrow 10am")]
})
print(result["messages"][-1].content)
```

### Via AI-ERP-Agent (with date parsing)

```python
from src.erp.agent import delegate_to_task_agent

# ERP agent handles "tomorrow", "this_week", etc.
result = delegate_to_task_agent.invoke({
    "request": "List tasks for tomorrow",
    "period": "tomorrow"
})
```

## Database Schema

```sql
CREATE TABLE api.ai_tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    due_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Configuration

Edit `config/.env`:

```env
POSTGRES_DB=ai-erp-database
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
OLLAMA_HOST=localhost
OLLAMA_MODEL=llama3.1:8b
```