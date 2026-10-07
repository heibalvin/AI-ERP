from typing import Literal
from datetime import datetime, timedelta
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from src.task.agent import build_task_agent

llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
web_search = DuckDuckGoSearchRun()

def parse_relative_date(period: str) -> tuple[str, str] | None:
    """Parse relative date periods into explicit start/end date strings."""
    now = datetime.now()
    
    if period == "tomorrow":
        tomorrow = now + timedelta(days=1)
        return (
            tomorrow.strftime("%Y-%m-%d 00:00:00"),
            tomorrow.strftime("%Y-%m-%d 23:59:59")
        )
    elif period == "today":
        return (
            now.strftime("%Y-%m-%d 00:00:00"),
            now.strftime("%Y-%m-%d 23:59:59")
        )
    elif period == "this_week" or period == "week":
        start_of_week = now - timedelta(days=now.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return (
            start_of_week.strftime("%Y-%m-%d 00:00:00"),
            end_of_week.strftime("%Y-%m-%d 23:59:59")
        )
    elif period == "next_week":
        start_of_week = now - timedelta(days=now.weekday()) + timedelta(weeks=1)
        end_of_week = start_of_week + timedelta(days=6)
        return (
            start_of_week.strftime("%Y-%m-%d 00:00:00"),
            end_of_week.strftime("%Y-%m-%d 23:59:59")
        )
    return None

def format_tasks_for_period(tasks: list[dict], period: str) -> str:
    """Format tasks for display based on the requested period."""
    if not tasks:
        return f"No tasks scheduled for {period}."
    
    if period == "tomorrow" or period == "today":
        lines = []
        for t in tasks:
            due = t.get("due_date")
            time_str = due.strftime("%H:%M") if isinstance(due, datetime) else "All day"
            desc = t.get('description', '')
            line = f"{time_str} : {t['title']}"
            if desc:
                line += f" - {desc}"
            lines.append(line)
        return "\n".join(lines)
    
    elif period in ("this_week", "week", "next_week"):
        grouped = {}
        for t in tasks:
            due = t.get("due_date")
            if isinstance(due, datetime):
                day_name = due.strftime("%A (%Y-%m-%d)")
                time_str = due.strftime("%H:%M")
            else:
                day_name = "Unscheduled"
                time_str = "All day"
            desc = t.get('description', '')
            task_line = f"{time_str}: {t['title']}"
            if desc:
                task_line += f" - {desc}"
            grouped.setdefault(day_name, []).append(task_line)
        
        output = []
        for day, items in grouped.items():
            output.append(f"\n{day}")
            output.extend(items)
        return "\n".join(output)
    
    else:
        return "\n".join([f"[{t['id']}] {t['title']} - Status: {t['status']} (Due: {t['due_date']})" for t in tasks])

@tool
def delegate_to_task_agent(request: str, period: str = None, start_date: str = None, end_date: str = None, status: str = None) -> str:
    """
    Delegates a task management request to the AI-Task-Agent sub-agent.
    The ERP agent handles date parsing and calls task agent tools directly with explicit parameters.
    """
    task_agent = build_task_agent()
    
    # If period is provided, parse it to explicit dates
    if period and not (start_date and end_date):
        parsed = parse_relative_date(period)
        if parsed:
            start_date, end_date = parsed
    
    # For query operations, call task agent tools directly with explicit parameters
    # This avoids LLM parameter extraction issues
    if "list" in request.lower() or "show" in request.lower() or "get" in request.lower():
        from src.task.tools import get_tasks_tool
        tasks = get_tasks_tool.invoke({
            "status": status,
            "start_date": start_date,
            "end_date": end_date
        })
        if period in ("tomorrow", "today", "this_week", "week", "next_week"):
            return format_tasks_for_period(tasks, period)
        else:
            return "\n".join([f"[{t['id']}] {t['title']} - Status: {t['status']} (Due: {t['due_date']})" for t in tasks]) if tasks else "No tasks found."
    
    # For mutations, use the task agent LLM
    enhanced_request = request
    if start_date and end_date:
        enhanced_request += f" (due between {start_date} and {end_date})"
    if status:
        enhanced_request += f" with status {status}"
    
    result = task_agent.invoke({"messages": [("user", enhanced_request)]})
    return result["messages"][-1].content

@tool
def search_internet(query: str) -> str:
    """Performs a web search for general queries when no sub-agent is available."""
    return web_search.run(query)

tools = [delegate_to_task_agent, search_internet]

def router_node(state: MessagesState):
    """Analyzes the user request and routes it or asks clarification questions."""
    system_prompt = (
        "You are AI-ERP-Agent, a central business assistant orchestrating domain sub-agents.\n"
        "Available sub-agents:\n"
        "- AI-Task-Agent (via delegate_to_task_agent tool) for creating, reading, and updating tasks.\n\n"
        "Guidelines:\n"
        "1. Identify the request type.\n"
        "2. If ambiguous, ask clarifying questions directly.\n"
        "3. Route task management requests using `delegate_to_task_agent`.\n"
        "   - For relative dates (tomorrow, today, this week, next_week), use the `period` parameter.\n"
        "   - For explicit date ranges, use `start_date` and `end_date` parameters.\n"
        "   - For status filtering, use the `status` parameter.\n"
        "4. For general or external queries without a sub-agent, use `search_internet` or answer directly.\n"
        "5. Once a sub-agent completes a task, summarize the result back to the user clearly."
    )
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]
    model_with_tools = llm.bind_tools(tools)
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

def build_erp_agent(checkpointer=None):
    workflow = StateGraph(MessagesState)
    workflow.add_node("router", router_node)
    workflow.add_node("tools", ToolNode(tools))

    workflow.add_edge(START, "router")
    workflow.add_conditional_edges("router", should_continue, ["tools", END])
    workflow.add_edge("tools", "router")

    return workflow.compile(checkpointer=checkpointer)