#!/usr/bin/env python3
import os
import logging
from strands import tool
from botocore.config import Config
from strands import Agent
from strands.models import BedrockModel
from strands_tools import use_computer
import os, time
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
    computer_agent = Agent(
            system_prompt=system_prompt,
            model=model,
            tools=[use_computer],
        )
    if "start my day" in query.lower():
        setup(computer_agent)
        # query = "we have just opened kiro and we are on it in full screen, can you click on open a project, then can you click on users, then click on jambrubu, then scroll down on the right side of menu, click on workplace, then click testing_ag_ui, then click open"
        #query = "we have slack open, can you click on the strands agents interest channel then right click on one of the messages, then click on reply in thread. from the thread info type a response but let me hit enter"
        return "\n💻 COMPUTER AGENT RESPONSE 💻\n\n✅ Daily setup has been successful! All the user needs to do is touch their security key and your computer should be ready for today's work! No further computer assistance is needed right now.\n"
    if "start demo record" in query.lower():
        print("entered dem record if statement")
        setup_recording(computer_agent)
        # Return immediately after setting up recording - no need to continue processing
        return "\n💻 COMPUTER AGENT RESPONSE 💻\n{'='*50}\n✅ Screen recording has been started successfully! Recording is now active.\n\n🎬 Screen Studio is now recording your screen.\n📹 Recording setup completed - you can proceed with your demo.\n\n⚠️  Note: The screen is recording and no further computer assistance is needed right now.\n{'='*50}"
    if "start focus mode" in query.lower():
        focus_mode(computer_agent)
        return "\n💻 COMPUTER AGENT RESPONSE 💻\n{'='*50}\n✅ Focus mode has been entered successfully! Note: Focus is entered, no further computer assistance is needed right now.\n{'='*50}"
    if "stop demo record" in query.lower():
        print("entered demo stop is statement")
        stop_recording(computer_agent)
        # Return immediately after stopping recording - no need to continue processing
        return "\n💻 COMPUTER AGENT RESPONSE 💻\n{'='*50}\n✅ Screen recording has been stopped successfully! Recording is now inactive.\n\n🎬 Screen Studio recording has been stopped.\n📹 Recording stop completed.\n\n⚠️  Note: Recording has ended and no further computer assistance is needed right now.\n{'='*50}"
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
        
        agent_response = computer_agent(formatted_query)
        text_response = str(agent_response)
        #if start_my_day==True:
        

        if len(text_response) > 0:
            return f"\n💻 COMPUTER AGENT RESPONSE 💻\n{'='*50}\n{text_response}\n{'='*50}"

        return "\033[1;31m❌ Error: No response received from the computer automation task\033[0m"
    except Exception as e:
        # Return specific error message for computer automation processing
        return f"Computer Automation Error: {str(e)}\nPlease check your request and try again."

    
def focus_mode(agent):
    agent.tool.use_computer(action="move_mouse", x=1344, y=17) #contol center
    time.sleep(.3)
    # agent.tool.use_computer(action="click", x=1360, y=18) 
    agent.tool.use_computer(action="click", x=1344, y=17)
    time.sleep(.5)
    agent.tool.use_computer(action="move_mouse",x=1386, y=86) #do not disturb
    agent.tool.use_computer(action="click",x=1386, y=86) #do not disturb
    time.sleep(.3)
    agent.tool.use_computer(action="open_app", app_name="clock") 
    time.sleep(1) 
    agent.tool.use_computer(action="hotkey", hotkey_str="ctrl+alt+right")
    time.sleep(.3)
    agent.tool.use_computer(action="click",x=1270, y=62) #timer
    time.sleep(.3)    
    # agent.tool.use_computer(action="click",x=1485, y=64) #add timer
    agent.tool.use_computer(action="move_mouse",x=1129, y=344) #number
    time.sleep(.3)   
    agent.tool.use_computer(action="click",x=1129, y=344) #number
    time.sleep(1)   
    agent.tool.use_computer(action="click",x=1129, y=344) #number 
    time.sleep(1)   
    agent.tool.use_computer(action="type", text="25")
    time.sleep(.3)    
    agent.tool.use_computer(action="click",x=1218, y=633) #start

 

def setup(agent):
    agent.tool.use_computer(action="open_app", app_name="Chrome")
    # # time.sleep(1) 
    
    # # time.sleep(1)
    agent.tool.use_computer(action="hotkey", hotkey_str="ctrl+alt")
    agent.tool.use_computer(action="hotkey", hotkey_str="ctrl+alt+right")
    # time.sleep(5) 

    # time.sleep(1)
    agent.tool.use_computer(action="move_mouse", x=860, y=136)
    time.sleep(2)
    agent.tool.use_computer(action="click", x=860, y=136)

    #click on plus button
    agent.tool.use_computer(action="move_mouse", x=1100, y=58)
    agent.tool.use_computer(action="click", x=1100, y=58)


    # agent.tool.use_computer(action="open_app", app_name="Chrome")
    # agent.tool.use_computer(action="hotkey", hotkey_str="ctrl+alt")
    # agent.tool.use_computer(action="hotkey", hotkey_str="command+t") 
    time.sleep(3)
    agent.tool.use_computer(action="type", text="merlon", app_name="Chrome")
    time.sleep(3)
    agent.tool.use_computer(action="key_press", key="enter")
 
    time.sleep(5)
    agent.tool.use_computer(action="open_app", app_name="Slack")
    time.sleep(1)
    agent.tool.use_computer(action="hotkey", hotkey_str="ctrl+alt+left")

    agent.tool.use_computer(action="hotkey", hotkey_str="command+g") 
    time.sleep(1)
    agent.tool.use_computer(action="type", text="stran")
    agent.tool.use_computer(action="click", x=225, y=120)

    time.sleep(1)

    
# VS Code Setup

    agent.tool.use_computer(action="open_app", app_name="Visual Studio Code")
    time.sleep(1)
    agent.tool.use_computer(action="hotkey", hotkey_str="ctrl+command+f")

    time.sleep(1)
 
# mwinit setup

    agent.tool.use_computer(action="open_app", app_name="iTerm")

    time.sleep(2)

    agent.tool.use_computer(action="click", x=135, y=18)
    agent.tool.use_computer(action="click", x=154, y=54)
    time.sleep(3)

    agent.tool.use_computer(action="open_app", app_name="iTerm")
    time.sleep(3)


    agent.tool.use_computer(action="type", text="mwinit")
    time.sleep(1)

    agent.tool.use_computer(action="key_press", app_name="iTerm", key="enter")
    time.sleep(2)

    agent.tool.use_computer(action="type", text="04132004")
    time.sleep(2)

    agent.tool.use_computer(action="key_press", key="enter")
 
 

def setup_recording(agent):
    agent.tool.use_computer(action="open_app", app_name="Screen Studio")
    agent.tool.use_computer(action="hotkey", app_name="Screen Studio", hotkey_str="option+command")
    agent.tool.use_computer(action="hotkey", app_name="Screen Studio", hotkey_str="option+command+3")
    # interactive_agent.tool.use_computer(action="hotkey", app_name="Screen Studio", hotkey_str="ctrl+command+shift+s")
    time.sleep(1)
    agent.tool.use_computer(action="click", x=747, y=547) 
    
    # interactive_agent.tool.use_computer(action="click", app_name="clock", x=1028, y=914)
def stop_recording(agent):
    agent.tool.use_computer(action="hotkey", app_name="Screen Studio", hotkey_str="option+command")
    agent.tool.use_computer(action="hotkey", app_name="Screen Studio", hotkey_str="ctrl+command+shift+s")
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
        elif user_input.lower() == "setup":
            setup(interactive_agent)
            user_input="you just setup my timer, thanks!"
        elif user_input.lower() == "start demo record":
            setup_recording(interactive_agent)
            user_input="you just set up and started recording my screen, thanks!"
            break
        elif user_input.lower() == "stop demo record":
            stop_recording(interactive_agent)
            break

            
        # Use ANSI color codes to make the agent's response stand out
        print("\n\033[1;36m--- Agent Response ---\033[0m")  # Cyan color, bold text
        # if knowledge_base_id:
        #     interactive_agent.tool.retrieve(text=user_input, knowledgeBaseId=knowledge_base_id)

        interactive_agent(user_input)

        print("\033[1;36m--- End of Response ---\033[0m\n")  # Cyan color, bold text
