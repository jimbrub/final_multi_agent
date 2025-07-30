from strands import Agent
from strands_tools import file_read, file_write, editor
from browser_agent import use_browser_agent
from use_computer_agent import use_computer_agent
from news_reporter_agent import news_reporter_agent
from diagram_builder_agent import diagram_builder_agent
import re


ORCHESTRATOR_SYSTEM_PROMPT = """
You are the Productivity Orchestrator, coordinating specialized AI agents to handle user requests efficiently.

ROUTING RULES:
- Computer automation tasks → use_computer_agent
- Web browsing & automation → use_browser_agent  
- News, RSS feeds, breaking news → news_reporter_agent
- Diagrams (UML, AWS architecture) → diagram_builder_agent

Always route requests to the appropriate specialist agent for optimal results.
"""

# Create a file-focused agent with selected tools
orchestrator_agent = Agent(
    system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
    callback_handler=None,
    # tools=[browser_agent, use_computer_agent, news_reporter_agent],
    tools=[use_browser_agent, news_reporter_agent, diagram_builder_agent, use_computer_agent],
)





if __name__ == "__main__":
    print("\n🚀 PRODUCTIVITY ORCHESTRATOR SYSTEM 🚀")
    print("="*60)
    print("🌐 Browser Agent    - Web automation & browsing")
    print("💻 Computer Agent   - Desktop automation & control")
    print("📰 News Reporter    - RSS feeds & breaking news")
    print("📊 Diagram Builder  - UML & AWS architecture diagrams")
    print("="*60)
    print("Type 'exit' to quit\n")

    # Interactive loop
    while True:
        try:
            user_input = input("🎯 > ")
            if user_input.lower() == "exit":
                print("\nGoodbye! 👋")
                break

            response = orchestrator_agent(user_input)
            print(str(response))
            
        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try asking a different question.")