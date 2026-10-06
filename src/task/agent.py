from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from src.task.tools import create_task_tool, list_tasks_by_period_tool, update_task_status_tool

def build_task_agent():
    llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
    tools = [create_task_tool, list_tasks_by_period_tool, update_task_status_tool]
    
    system_prompt = (
        "You are AI-Task-Agent, managing task schedules in PostgreSQL.\n"
        "Formatting instructions:\n"
        "1. When listing tasks for TOMORROW, present each line as 'HH:MM : task description'.\n"
        "2. When listing tasks for the WEEK, group them by Day Name, followed by 'HH:MM: task description' indented beneath."
    )
    
    return create_react_agent(llm, tools=tools, prompt=system_prompt)