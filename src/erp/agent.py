from typing import Literal
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from src.task.agent import build_task_agent

llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
web_search = DuckDuckGoSearchRun()

@tool
def delegate_to_task_agent(request: str) -> str:
    """Delegates a task management request to the AI-Task-Agent sub-agent."""
    task_agent = build_task_agent()
    result = task_agent.invoke({"messages": [("user", request)]})
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