from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from src.task.tools import create_task_tool, get_tasks_tool, update_task_status_tool, delete_task_tool

def build_task_agent():
    llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
    tools = [create_task_tool, get_tasks_tool, update_task_status_tool, delete_task_tool]
    
    system_prompt = (
        "You are AI-Task-Agent, a sub-agent managing tasks directly in PostgreSQL (api.ai_tasks).\n\n"
        "Rules:\n"
        "1. Always use database tools to execute requested CRUD operations.\n"
        "2. Do not attempt to compute relative dates (e.g., 'tomorrow', 'this week') yourself; "
        "execute queries using the parameters provided.\n"
        "3. Return task data concisely as structured feedback from tool executions."
    )
    
    return create_react_agent(llm, tools=tools, prompt=system_prompt)