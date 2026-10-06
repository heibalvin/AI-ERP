from src.db import get_checkpointer
from src.erp.agent import build_erp_agent

def main():
    print("=== AI-ERP-Agent Initialized ===")
    
    # Initialize checkpointer for persistent memory across runs
    checkpointer = get_checkpointer()
    erp_agent = build_erp_agent(checkpointer=checkpointer)
    
    thread_config = {"configurable": {"thread_id": "session_001"}}

    while True:
        try:
            user_input = input("\nUser > ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input:
                continue

            events = erp_agent.stream(
                {"messages": [("user", user_input)]},
                config=thread_config,
                stream_mode="values"
            )

            for event in events:
                last_msg = event["messages"][-1]
                if last_msg.type == "ai" and last_msg.content:
                    print(f"\nAI-ERP-Agent > {last_msg.content}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()