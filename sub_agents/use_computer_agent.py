#!/usr/bin/env python3
import os
import logging
from strands import tool
from botocore.config import Config
from strands import Agent
from strands.models import BedrockModel
from strands_tools import use_computer
import os
# from strands_agents_builder.utils.kb_utils import load_system_prompt, store_conversation_in_kb

# Configure logging to show INFO level logs
logging.basicConfig(
    level=logging.INFO,
    format='\033[90m%(asctime)s - %(name)s - %(levelname)s - %(message)s\033[0m',
    datefmt='%Y-%m-%d %H:%M:%S'
)
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0", max_tokens=65536, # max 65536 ---> suggested
    boto_client_config=Config(
        read_timeout=900,
        connect_timeout=900,
        retries=dict(max_attempts=3, mode="adaptive"),
    ),
    additional_request_fields={
        "anthropic_beta": ["interleaved-thinking-2025-05-14", "computer-use-2025-01-24"],  # Enable computer use beta
        "thinking": {
            "type": os.getenv("STRANDS_THINKING_TYPE", "enabled"),
            "budget_tokens": int(os.getenv("STRANDS_BUDGET_TOKENS", "2048")),
        },
    },
)
knowledge_base_id = os.getenv("STRANDS_KNOWLEDGE_BASE_ID")

system_prompt = """
Always set send_screenshot=true

for opening apps use the tools open_app action

CRITICAL INSTRUCTION FOR COMPUTER INTERACTION:

1. OCR RESULTS ARE ABSOLUTE TRUTH
   - The text and coordinates from analyze_screen are your primary source of information
   - You MUST use both the exact text and coordinates provided by OCR
   - Never substitute or paraphrase OCR-detected text with your own interpretation

2. USING OCR RESULTS (Strictly enforced in this order):
   a. Exact Text Match: If the exact text you need is detected by OCR, use its coordinates
   b. Partial Text Match: If your target is part of detected OCR text, use those coordinates
   c. Only if NO text match exists:
      - Interpolate based on nearby OCR-detected text and coordinates
      - Clearly explain why you couldn't find a text match in OCR results

3. MANDATORY STEPS BEFORE ANY ACTION:
   1. Run analyze_screen
   2. List ALL text detected by OCR, with their coordinates
   3. Search this list for your target text or related text
   4. If found, use EXACTLY as detected (text and coordinates)
   5. If not found, state "Target text '[exact target]' not found in OCR results" before estimating

4. ERROR PREVENTION:
   - If you're not using text exactly as detected by OCR, STOP and reassess
   - Never rephrase or summarize OCR-detected text; use it verbatim
   - OCR results supersede any visual interpretation or prior knowledge

5. SCREENSHOTS ARE SECONDARY
   - Use screenshots (if provided) only to understand context, never to override OCR data
   - If OCR and visual interpretation conflict, OCR is always correct

Remember: Your primary task is to use the OCR-detected text and coordinates. Any deviation from this is considered an error in your operation.
"""

@tool
def use_computer_agent(query: str) -> str:
    """
    Process and execute computer automation tasks using screen analysis and interaction.
    
    Args:
        query: A computer automation request from the user, which can include:
            - Application control
            - GUI navigation and interaction
            - Text input and extraction
            - File management
            - System monitoring
            - Calendar and scheduling analysis
            - Screenshot interpretation
            
    Returns:
        A detailed response describing the executed actions, results, and any relevant
        extracted information. In case of errors, returns explanatory error messages
        with suggested alternatives.
    """
    # Format the query for the computer use agent with clear instructions
    os.environ["BYPASS_TOOL_CONSENT"] = "true"  
    formatted_query = f"""
    Please help me with the following computer automation task. Remember to:
    1. Analyze screen elements carefully before interactions
    2. Use precise coordinate data for clicking
    3. Follow proper keyboard shortcut conventions for Mac
    4. Provide clear progress updates

    User Request: {query}
    """
    
    try:
        print("Executing Computer Automation Task")
        # Create the computer use agent with use_computer capability
        computer_agent = Agent(
            system_prompt=system_prompt,
            model=model,
            tools=[use_computer],
        )
        agent_response = computer_agent(formatted_query)
        text_response = str(agent_response)

        if len(text_response) > 0:
            return f"\n💻 COMPUTER AGENT RESPONSE 💻\n{'='*50}\n{text_response}\n{'='*50}"

        return "\033[1;31m❌ Error: No response received from the computer automation task\033[0m"
    except Exception as e:
        # Return specific error message for computer automation processing
        return f"Computer Automation Error: {str(e)}\nPlease check your request and try again."

        
# Interactive loop for standalone usage
if __name__ == "__main__":
    print(f"\n\033[1;36m🌟 Computer Automation Agent 🌟\033\n")
    print("Available commands:")
    print("  • Type your message for the agent")
    print("  • 'exit' - Quit the program")
    print("")

    # Create a direct instance for interactive use
    interactive_agent = Agent(system_prompt=system_prompt, model=model, tools=[use_computer])

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

        print("\033[1;36m--- End of Response ---\033[0m\n")  # Cyan color, bold text
