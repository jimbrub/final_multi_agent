#!/usr/bin/env python3
import os
import sys
import logging
import argparse
from strands import tool


from botocore.config import Config
from strands import Agent
from strands.models import BedrockModel
from strands_tools import http_request, speak, use_browser, memory 
import sys
import os

# Configure logging to reduce noise while keeping errors
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors
    format='\033[90m%(asctime)s - %(name)s - %(levelname)s - %(message)s\033[0m',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Specifically suppress verbose loggers from Strands tools
logging.getLogger('strands.telemetry.metrics').setLevel(logging.ERROR)
logging.getLogger('strands_tools.use_browser').setLevel(logging.ERROR)
logging.getLogger('strands').setLevel(logging.WARNING)
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0", max_tokens=10000, # max 65536 ---> suggested
    boto_client_config=Config(
        read_timeout=900,
        connect_timeout=900,
        retries=dict(max_attempts=3, mode="adaptive"),
    ),
    additional_request_fields={
        "anthropic_beta": ["interleaved-thinking-2025-05-14"],  # Enable computer use beta
        "thinking": {
            "type": os.getenv("STRANDS_THINKING_TYPE", "enabled"),
            "budget_tokens": int(os.getenv("STRANDS_BUDGET_TOKENS", "2048")),
        },
    },
)

system_prompt = """
You are an advanced Browser AI Agent with web automation capabilities. You execute web tasks with precision and reliability, following these core principles:

CAPABILITIES:
- Web navigation and interaction (browsing, clicking, form-filling)
- Multi-tab management and coordination
- Data extraction and analysis
- JavaScript execution and page manipulation
- Screenshot capture
- HTTP request handling

EXECUTION PROTOCOL:
1. Analysis Phase
- Examine page structure using get_html before any interaction
- Verify element presence using JavaScript evaluation
- Never assume selector validity without verification
- Plan multi-step operations before execution

2. Interaction Guidelines
- Use explicit tab IDs for all operations
- Maintain clear tab state tracking
- Verify form fields before submission
- Handle pagination systematically
- Clean up resources after task completion

3. Error Management
- Implement fallback strategies (e.g., DuckDuckGo if Google blocks)
- Handle CAPTCHAs and anti-automation measures
- Provide clear error explanations and alternatives
- Verify success of each action before proceeding

4. Data Handling
- Extract data using precise selectors
- Validate extracted information
- Structure output clearly and consistently
- Implement proper pagination handling

OPERATING SEQUENCE:
1. Analyze user request
2. Verify prerequisites
3. Plan execution steps
4. Execute with verification
5. Provide progress updates
6. Handle errors gracefully
7. Clean up resources

INTERACTION STYLE:
- Maintain clear communication
- Explain actions being taken
- Provide status updates
- Request clarification when needed
- Suggest optimizations when applicable

Priority: Accuracy and reliability over speed. Always verify before acting.


"""


# Initialize the Strands Agent with Computer Use capabilities and speech
    

@tool
def use_browser_agent(query: str) -> str:
    """
    Process and execute web browsing tasks using an automated browser agent.
    
    Args:
        query: A web automation request from the user, which can include:
            - Web navigation
            - Form filling
            - Data extraction
            - Multi-tab operations
            - Web scraping
            - Screenshot capture
            - Element interaction
            
    Returns:
        A detailed response describing the executed actions, results, and any relevant
        extracted information. In case of errors, returns explanatory error messages
        with suggested alternatives.
    """
    # Format the query for the math agent with clear instructions
    os.environ["BYPASS_TOOL_CONSENT"] = "true"
    print("routed to browser agent")
    formatted_query = f"""
    Please help me with the following web automation task. Remember to:
    1. Analyze the page structure before interactions
    2. Use proper element discovery
    3. Maintain explicit tab management
    4. Provide clear progress updates

    User Request: {query}
    """
    
    try:
        print("Executing Browser Automation Task")
        # Create the math agent with calculator capability
        browser_agent = Agent(
            system_prompt=system_prompt,
            model=model,
            tools=[use_browser, http_request, memory],
        )
        agent_response = browser_agent(formatted_query)
        text_response = str(agent_response)

        if len(text_response) > 0:
            return f"\n🌐 BROWSER AGENT RESPONSE 🌐\n{'='*50}\n{text_response}\n{'='*50}"

        return "\033[1;31m❌ Error: No response received from the browser automation task\033[0m"
    except Exception as e:
        # Return specific error message for math processing
        return f"Browser Automation Error: {str(e)}\nPlease check your request and try again."


def start_research(agent):
    """Start research mode by opening browser and navigating to DuckDuckGo"""
    agent("Open Chromium browser and navigate to duckduckgo.com for research")

if __name__ == "__main__":
    print(f"\n\033[1;36m🌟 Browser Automation Agent 🌟\033\n")
    print("Available commands:")
    print("  • Type your message for the agent")
    print("  • 'exit' - Quit the program")
    print("")

    # Create a direct instance for interactive use
    interactive_agent = Agent(system_prompt=system_prompt, model=model, tools=[use_browser, memory])

    while True:
        user_input = input("\n\033[1;33m> \033[0m")  # Yellow prompt
        
        if user_input.lower() == "exit":
            print("\n\033[1;36mGoodbye! 👋\033[0m")
            break
        if user_input.lower() == "research mode":
            start_research(interactive_agent)
            break
            
        print("\n\033[1;36m--- Agent Response ---\033[0m")  # Cyan color, bold text

        interactive_agent(user_input)

        print("\033[1;36m--- End of Response ---\033[0m\n")  # Cyan color, bold text