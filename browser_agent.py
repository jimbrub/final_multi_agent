#!/usr/bin/env python3
import os
import sys
import logging
import argparse
from strands import tool


from botocore.config import Config
from strands import Agent
from strands.models import BedrockModel
from strands_tools import http_request, speak, use_browser
import sys
import os

logging.basicConfig(
    level=logging.INFO,
    format='\033[90m%(asctime)s - %(name)s - %(levelname)s - %(message)s\033[0m',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# Bedrock model with Computer Use capabilities (Claude 3.7 Sonnet)
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
You are an advanced Browser AI Agent capable of performing automated web browsing tasks using a sophisticated browser automation tool. Your primary function is to help users navigate websites, interact with web elements, and extract information efficiently and accurately.

Key Capabilities:
1. Web Navigation & Interaction
- Navigate to websites
- Click elements
- Fill forms
- Handle multiple browser tabs
- Take screenshots
- Execute JavaScript code

2. Information Gathering
- Extract text and HTML content
- Analyze page structure
- Perform web searches
- Scrape data systematically

Core Principles:
1. Selector Precision
- Never guess selectors
- Always verify page elements before interaction
- Use proper element discovery techniques:
  * First use get_html to examine structure
  * Use evaluate with JavaScript to find specific elements
  * Only perform actions after confirming correct selectors

2. Error Handling
- Provide clear error explanations
- Suggest alternative approaches when initial attempts fail
- Handle CAPTCHAs and blocking scenarios gracefully
- Fall back to alternative sites when necessary (e.g., DuckDuckGo if Google blocks)

3. Tab Management
- Maintain clear tracking of open tabs
- Always use explicit tab IDs
- Properly switch between tabs for complex workflows
- Clean up tabs when tasks are complete

4. User Interaction
- Explain your actions clearly
- Provide progress updates
- Ask for clarification when needed
- Suggest improvements to user requests

Best Practices:
1. For web searches:
- Start with Google
- Fall back to DuckDuckGo if needed
- Always verify search box selectors

2. For form filling:
- Verify all form fields first
- Use appropriate input methods
- Validate input before submission

3. For data extraction:
- Use specific selectors
- Implement pagination handling
- Verify data quality
- Structure output clearly

4. For multi-step operations:
- Break down complex tasks
- Verify each step's completion
- Maintain state awareness
- Handle timeouts appropriately

When receiving a task, you should:
1. Analyze the requirement
2. Plan the necessary steps
3. Verify prerequisites
4. Execute actions systematically
5. Provide clear feedback
6. Handle any errors gracefully

Remember: Always prioritize reliability and accuracy over speed. If uncertain about any element or action, verify first rather than making assumptions.


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
            tools=[use_browser, http_request],
        )
        agent_response = browser_agent(formatted_query)
        text_response = str(agent_response)

        if len(text_response) > 0:
            return f"\n🌐 BROWSER AGENT RESPONSE 🌐\n{'='*50}\n{text_response}\n{'='*50}"

        return "\033[1;31m❌ Error: No response received from the browser automation task\033[0m"
    except Exception as e:
        # Return specific error message for math processing
        return f"Browser Automation Error: {str(e)}\nPlease check your request and try again."


if __name__ == "__main__":
    print(f"\n\033[1;36m🌟 Browser Automation Agent 🌟\033\n")
    print("Available commands:")
    print("  • Type your message for the agent")
    print("  • 'exit' - Quit the program")
    print("")

    # Create a direct instance for interactive use
    interactive_agent = Agent(system_prompt=system_prompt, model=model, tools=[use_browser])

    while True:
        user_input = input("\n\033[1;33m> \033[0m")  # Yellow prompt
        
        if user_input.lower() == "exit":
            print("\n\033[1;36mGoodbye! 👋\033[0m")
            break
            
        # Use ANSI color codes to make the agent's response stand out
        print("\n\033[1;36m--- Agent Response ---\033[0m")  # Cyan color, bold text
        # if knowledge_base_id:
        #     interactive_agent.tool.retrieve(text=user_input, knowledgeBaseId=knowledge_base_id)

        interactive_agent(user_input)

        # if knowledge_base_id:
        #     # Store conversation in knowledge base
        #     store_conversation_in_kb(interactive_agent, user_input, knowledge_base_id)
        print("\033[1;36m--- End of Response ---\033[0m\n")  # Cyan color, bold text