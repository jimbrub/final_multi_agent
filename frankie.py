#!/usr/bin/env python3
"""
🤖 F.R.A.N.K.I.E. - Premium Multi-Agent Productivity System
===========================================================
Flexible Responsive Agent for Navigation Knowledge Integration and Execution

SYSTEM OVERVIEW:
F.R.A.N.K.I.E. is an intelligent orchestration system that coordinates multiple
specialized AI agents to handle complex user requests. Features a premium CLI
interface with rich visual components, real-time feedback, and professional UX.

PREMIUM FEATURES:
- Rich typography with panels, tables, and markdown rendering
- Advanced spinner system with per-tool progress tracking
- Professional welcome system with dynamic status updates
- Shell command integration with ! prefix
- Enhanced error reporting with suggestions
- Real-time agent coordination feedback
"""

import argparse
import time
import sys
import os
from datetime import datetime
from pathlib import Path

# Rich components for premium UI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.align import Align
from rich.box import ROUNDED
from rich.theme import Theme
from rich.status import Status
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text
from rich.live import Live

# Halo for advanced spinners
from halo import Halo
from colorama import Fore, Style, init

# Strands imports
from strands import Agent
from strands_tools import file_read, file_write, editor, rss, retrieve, slack, diagram, mcp_client, current_time, memory
from strands_tools.shell import shell
# Agent imports
from sub_agents.browser_agent import use_browser_agent
from sub_agents.use_computer_agent import use_computer_agent
from sub_agents.content_generator_agent import content_generator_agent
# from additional_tools_agent import additional_tools_agent
from sub_agents.memory_brain_agent import use_memory_brain_agent
from sub_agents.coding_buddy_agent import coding_agent

# Initialize colorama
init(autoreset=True)

# Premium theme for consistent styling
FRANKIE_THEME = Theme({
    "info": "dim cyan",
    "warning": "yellow",
    "danger": "bold red",
    "success": "green",
    "heading": "bold blue",
    "subheading": "cyan",
    "highlight": "magenta",
    "prompt": "bold green",
    "agent": "bold yellow",
    "system": "dim blue",
})

# Create premium console
console = Console(theme=FRANKIE_THEME)

class PremiumSpinnerManager:
    """Advanced spinner management for premium UX"""
    
    def __init__(self):
        self.current_spinner = None
        self.tool_histories = {}
        
    def start_thinking(self, message="🧠 Analyzing request..."):
        """Start thinking spinner with Rich status"""
        if self.current_spinner:
            self.current_spinner.stop()
        self.current_spinner = Status(f"[blue]{message}[/blue]", spinner="dots", console=console)
        self.current_spinner.start()
    
    def start_tool_spinner(self, tool_name, message="Preparing..."):
        """Start tool-specific spinner with Halo"""
        if self.current_spinner:
            self.current_spinner.stop()
        
        spinner_text = f"🛠️  {tool_name}: {message}"
        self.current_spinner = Halo(
            text=spinner_text,
            spinner='dots',
            color='green',
            text_color='green'
        )
        self.current_spinner.start()
    
    def update_tool_progress(self, tool_name, message):
        """Update tool progress"""
        if self.current_spinner and hasattr(self.current_spinner, 'text'):
            self.current_spinner.text = f"🛠️  {tool_name}: {message}"
    
    def succeed_tool(self, tool_name, message, duration=None):
        """Mark tool as successful"""
        if self.current_spinner and hasattr(self.current_spinner, 'succeed'):
            final_message = f"🛠️  {tool_name}: {message}"
            if duration:
                final_message += f" ({duration:.2f}s)"
            self.current_spinner.succeed(final_message)
            self.current_spinner = None
    
    def fail_tool(self, tool_name, error, duration=None):
        """Mark tool as failed"""
        if self.current_spinner and hasattr(self.current_spinner, 'fail'):
            final_message = f"🛠️  {tool_name}: {error}"
            if duration:
                final_message += f" ({duration:.2f}s)"
            self.current_spinner.fail(final_message)
            self.current_spinner = None
    
    def stop(self):
        """Stop all spinners"""
        if self.current_spinner:
            if hasattr(self.current_spinner, 'stop'):
                self.current_spinner.stop()
            self.current_spinner = None

# Global spinner manager
spinner_manager = PremiumSpinnerManager()

# Research mode state management
research_mode_active = False
research_mode_setup_complete = False

def get_system_status():
    """Generate rich system status for premium banner"""
    current_time_str = datetime.now().strftime("%H:%M:%S")
    
    # Create status table
    status_table = Table.grid(padding=1)
    status_table.add_column(justify="center")
    status_table.add_column(justify="center")
    status_table.add_column(justify="center")
    
    status_table.add_row(
        "[green]✅ RSS Feeds Ready[/green]",
        "[blue]🔧 All Tools Available[/blue]", 
        f"[yellow]⏰ Ready at {current_time_str}[/yellow]"
    )
    
    return status_table

def render_premium_welcome():
    """Render premium welcome message using Rich components"""
    
    # System status
    status = get_system_status()
    
    # Agent capabilities table
    agents_table = Table(title="🤖 Specialized Agent Capabilities", box=ROUNDED, show_header=True)
    agents_table.add_column("Agent", style="bold yellow", width=20)
    agents_table.add_column("Capabilities", style="cyan")
    
    agents_table.add_row("🌐 Browser Agent", "Web automation, scraping & interaction")
    agents_table.add_row("💻 Computer Agent", "Desktop control & automation") 
    agents_table.add_row("🧠 Memory Brain", "Knowledge storage & retrieval system")
    agents_table.add_row("👨‍💻 Coding Agent", "Software development, code analysis & terminal/file operations")
    agents_table.add_row("✍️ Content Generator", "Diagrams, documents & visual content creation")
    
    # Features panel
    features_md = """
### 🎯 **Smart Features**
- **Intelligent Routing**: Automatically selects the best agent for your request
- **Direct Access**: Streamlined desktop automation without barriers  
- **Persistent Memory**: Remembers your preferences and context across sessions
- **Real-time Feedback**: Professional progress indicators and status updates
- **Computer Shortcuts**: Quick access to common automation tasks

### 💡 **Quick Start**
- Use natural language for any request - F.R.A.N.K.I.E. will route it optimally
- Type `help` for complete command reference and examples
- Type `shortcuts` to view computer automation quick actions
- Use `!` prefix for direct shell commands (e.g., `!ls -la`)
- Type `exit` to safely shutdown the system
    """
    
    # Create main welcome panel
    welcome_content = Align.center(
        Panel(
            Align.center(agents_table),
            title="[heading]🤖 F.R.A.N.K.I.E. Multi-Agent System[/heading]",
            subtitle="[info]Intelligent Agent Orchestration Platform[/info]",
            border_style="blue",
            box=ROUNDED,
            padding=(1, 2)
        )
    )
    
    # System status panel
    status_panel = Panel(
        Align.center(status),
        title="[success]🚀 System Status[/success]",
        border_style="green",
        box=ROUNDED
    )
    
    # Features panel
    features_panel = Panel(
        Markdown(features_md),
        title="[highlight]✨ Features & Quick Start[/highlight]",
        border_style="magenta", 
        box=ROUNDED
    )
    
    # Print all components
    console.print()
    console.print(welcome_content)
    console.print()
    console.print(status_panel)
    console.print()
    console.print(features_panel)
    console.print()

def show_shortcuts_menu():
    """Display computer agent shortcuts in a premium menu format"""
    
    # Computer shortcuts table
    shortcuts_table = Table(title="💻 Computer Agent Quick Actions", box=ROUNDED, show_header=True)
    shortcuts_table.add_column("Shortcut Command", style="bold yellow", width=25)
    shortcuts_table.add_column("Description", style="cyan", width=40)
    shortcuts_table.add_column("What It Does", style="green")
    
    shortcuts_table.add_row(
        "start my day", 
        "🌅 Morning productivity setup",
        "Opens Chrome, Slack, Outlook, VS Code"
    )
    shortcuts_table.add_row(
        "start demo record", 
        "🎬 Begin screen recording",
        "Launches Screen Studio and starts recording"
    )
    shortcuts_table.add_row(
        "stop demo record", 
        "⏹️ End screen recording", 
        "Stops Screen Studio recording session"
    )
    shortcuts_table.add_row(
        "start focus mode", 
        "🎯 Enter focus session",
        "Enables Do Not Disturb + 25min timer"
    )
    shortcuts_table.add_row(
        "play my music", 
        "🎵 Launch music player",
        "Opens Music app and starts playing"
    )
    shortcuts_table.add_row(
        "start presentation",
        "📽️ Launch presentation mode",
        "Opens PowerPoint and starts presentation"
    )
    shortcuts_table.add_row(
        "research mode",
        "🔬 Multi-step research with Quip option",
        "Opens browser, researches topic, optional Quip documentation"
    )
    
    # Usage instructions
    usage_md = """
### 🎯 **How to Use Computer Shortcuts**

**🚀 Automatic Routing:**
Simply type any of the shortcut commands above, and F.R.A.N.K.I.E. will **automatically detect and route** them to the Computer Agent for instant execution.

**Examples:**
- `start my day` - Perfect for morning routine
- `start demo record` - Quick demo recording setup  
- `start focus mode` - Pomodoro-style focus session
- `play my music` - Launch music app instantly

### ⚡ **Natural Language Support**
These commands work with natural language variations too:
- "Can you start my day setup?" ✅ Auto-routed
- "Please begin demo recording" ✅ Auto-routed  
- "I want to enter focus mode" ✅ Auto-routed
- "Open music please" ✅ Auto-routed

### 🎮 **Explicit Agent Routing**
Want to combine with other agents? Use explicit routing:
- `send computer start demo record, then use browser to go to wordle`
- `use computer agent to start focus mode, then route to coding agent`

**Key:** Shortcuts are auto-routed UNLESS you use explicit routing words like:
- "send computer..."
- "use computer agent..."
- "route to computer..."
    """
    
    # Print shortcuts components
    console.print()
    console.print(Panel(
        Align.center("[bold magenta]🚀 F.R.A.N.K.I.E. Computer Shortcuts Menu[/bold magenta]"),
        border_style="magenta",
        box=ROUNDED,
        padding=(1, 2)
    ))
    console.print()
    console.print(shortcuts_table)
    console.print()
    console.print(Panel(
        Markdown(usage_md),
        title="[highlight]📖 Usage Guide[/highlight]",
        border_style="blue",
        box=ROUNDED
    ))
    console.print()

def show_premium_help():
    """Display premium help with Rich formatting"""
    
    # Available agents
    agents_table = Table(title="🤖 Available Agents", box=ROUNDED)
    agents_table.add_column("Agent", style="bold yellow")
    agents_table.add_column("Specialization", style="cyan")
    agents_table.add_column("Example Commands", style="green")
    
    agents_table.add_row(
        "🌐 Browser", 
        "Web automation", 
        '"Browse to example.com and extract links"'
    )
    agents_table.add_row(
        "💻 Computer", 
        "Desktop control", 
        '"Take a screenshot", "Open calculator"'
    )
    agents_table.add_row(
        "👨‍💻 Coding", 
        "Development & Files", 
        '"Review code", "Look at files", "Check log contents"'
    )
    agents_table.add_row(
        "🧠 Memory", 
        "Knowledge storage", 
        '"Remember my Python preferences"'
    )
    agents_table.add_row(
        "✍️ Content", 
        "Diagrams & documents", 
        '"Create AWS architecture diagram", "Generate documentation"'
    )
    
    # System commands
    commands_table = Table(title="⌨️ System Commands", box=ROUNDED)
    commands_table.add_column("Command", style="bold yellow")
    commands_table.add_column("Description", style="cyan")
    
    commands_table.add_row("help", "Show this comprehensive guide")
    commands_table.add_row("shortcuts", "Show computer shortcuts menu")
    commands_table.add_row("clear", "Clear screen and show banner")  
    commands_table.add_row("exit", "Safely quit F.R.A.N.K.I.E.")
    commands_table.add_row("!<command>", "Execute shell command directly")
    commands_table.add_row("Ctrl+C", "Emergency exit with confirmation")
    
    # Print help components
    console.print()
    console.print(Panel(
        Align.center("[bold blue]F.R.A.N.K.I.E. Help & Command Reference[/bold blue]"),
        border_style="blue",
        box=ROUNDED
    ))
    console.print()
    console.print(agents_table)
    console.print()
    console.print(commands_table)
    console.print()
    
    # Tips panel
    tips_md = """
### 🚀 **Pro Tips**
- **Natural Language**: Just describe what you want - F.R.A.N.K.I.E. handles the routing
- **Shell Integration**: Use `!` prefix for direct shell access (e.g., `!git status`)  
- **Context Aware**: Memory agent remembers your preferences across sessions
- **Multi-step Tasks**: Describe complex workflows - agents coordinate automatically
- **Real-time Feedback**: Watch spinners for progress updates during execution
- **Computer Shortcuts**: Type shortcuts directly for instant auto-routing to Computer Agent
- **Explicit Routing**: Use "send computer..." for multi-agent workflows

### 🎯 **Best Practices**  
- Be specific about desired outcomes for better agent selection
- Use the memory agent to store important preferences and context
- Combine agents for complex tasks (e.g., "Research topic X and create a diagram")
- Use computer shortcuts for common productivity workflows
- Use explicit routing when combining shortcuts with other agent tasks

### ⚡ **Shortcut Examples**
- Direct: `start demo record` → Auto-routes to Computer Agent
- Explicit: `send computer start demo record, then use browser to go to wordle`
    """
    
    console.print(Panel(
        Markdown(tips_md),
        title="[highlight]💡 Tips & Best Practices[/highlight]",
        border_style="magenta",
        box=ROUNDED
    ))

def format_premium_response(response, agent_name="F.R.A.N.K.I.E."):
    """Format agent responses with premium styling"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    response_text = str(response)
    
    # Create response panel
    response_panel = Panel(
        response_text,
        title=f"[success]🤖 {agent_name} Response[/success] [system]│ {timestamp}[/system]",
        border_style="green",
        box=ROUNDED,
        padding=(1, 2)
    )
    
    console.print()
    console.print(response_panel)
    console.print()

def handle_shell_command(command):
    """Handle shell commands with premium feedback"""
    spinner_manager.start_tool_spinner("Shell", f"Executing: {command}")
    
    try:
        start_time = time.time()
        result = shell(command=command, non_interactive=True)
        duration = time.time() - start_time
        
        spinner_manager.succeed_tool("Shell", "Command executed", duration)
        
        # Format shell output
        if isinstance(result, dict) and result.get("status") == "success":
            console.print()
            console.print(Panel(
                str(result.get("content", [{}])[0].get("text", "")),
                title=f"[system]$ {command}[/system]",
                border_style="dim blue",
                box=ROUNDED
            ))
        else:
            console.print()
            console.print(Panel(
                f"[danger]Error executing command: {result}[/danger]",
                title=f"[danger]$ {command}[/danger]",
                border_style="red"
            ))
    except Exception as e:
        duration = time.time() - start_time if 'start_time' in locals() else 0
        spinner_manager.fail_tool("Shell", f"Error: {str(e)}", duration)

def detect_shortcut(user_input):
    """
    Detect if user input contains a computer shortcut.
    Returns the shortcut command if found, None otherwise.
    
    Does NOT intercept explicit agent routing commands.
    """
    input_lower = user_input.lower().strip()
    
    # Define computer shortcuts
    computer_shortcuts = [
        "start my day",
        "start demo record", 
        "stop demo record",
        "start focus mode",
        "play my music",
        "start presentation",
        "research mode"
    ]
    
    # Check if it's an explicit routing command - if so, don't intercept
    explicit_routing_patterns = [
        "send computer",
        "use computer", 
        "route to computer",
        "computer agent",
        "send to computer",
        "ask computer"
    ]
    
    # If it contains explicit routing, don't intercept
    for pattern in explicit_routing_patterns:
        if pattern in input_lower:
            return None
    
    # Check for direct shortcut matches
    for shortcut in computer_shortcuts:
        if input_lower == shortcut:
            return shortcut
    
    # Check for natural language variations that should be auto-routed
    natural_variations = {
        "start my day": [
            "start my morning setup",
            "begin my day",
            "morning setup",
            "daily startup",
            "morning routine"
        ],
        "start demo record": [
            "start recording a demo",
            "begin demo recording", 
            "record a demo",
            "start demo capture",
            "initiate demo recording"
        ],
        "stop demo record": [
            "stop recording demo",
            "end demo recording",
            "stop demo capture", 
            "finish recording"
        ],
        "start focus mode": [
            "enter focus mode",
            "begin focus session",
            "start focus session",
            "focus mode please"
        ],
        "play my music": [
            "open music",
            "start music",
            "launch music app",
            "open the music app",
            "play music",
            "start playing music",
            "music please"
        ]
    }
    
    # Check natural language variations
    for base_shortcut, variations in natural_variations.items():
        for variation in variations:
            if variation in input_lower:
                return base_shortcut
    
    return None

def handle_research_mode_workflow():
    """Handle the multi-step research mode workflow - clean agent output"""
    
    try:
        # Step 1: Browser Agent opens Chromium and DuckDuckGo
        # Let browser agent handle its own output naturally without F.R.A.N.K.I.E. interference
        browser_response = use_browser_agent("Open Chromium browser and navigate to duckduckgo.com. Wait for the page to load and be ready for research.")
        
        # Step 2: Computer Agent sets up research environment  
        # Let computer agent handle its own output naturally without F.R.A.N.K.I.E. interference
        computer_response = use_computer_agent("research mode")
        
        # Only F.R.A.N.K.I.E. message: Simple completion notice
        console.print()
        console.print(Panel(
            "[bold green]🎯 Research Mode Complete![/bold green]\n\n"
            "[bold yellow]Please tell me what topic you'd like to research![/bold yellow]\n\n"
            "[dim]Note: After research, you'll have the option to document findings in Quip.[/dim]",
            title="[highlight]📋 Ready for Research Topic[/highlight]",
            border_style="green",
            box=ROUNDED,
            padding=(1, 2)
        ))
        
        # Set global flag to indicate research mode setup is complete
        global research_mode_setup_complete
        research_mode_setup_complete = True
        
        return True
        
    except Exception as e:
        # Only show F.R.A.N.K.I.E. error handling if something fails
        console.print()
        console.print(Panel(
            f"[danger]Error setting up research mode:[/danger]\n[danger]Error:[/danger] {str(e)}\n\n"
            "[warning]💡 Falling back to computer agent research mode setup...[/warning]",
            title="[danger]❌ Research Mode Error[/danger]",
            border_style="red",
            box=ROUNDED,
            padding=(1, 2)
        ))
        
        # Fallback to just computer agent setup
        return fallback_to_computer_research_mode()

def fallback_to_computer_research_mode():
    """Fallback to just computer agent research mode if browser setup fails"""
    
    try:
        # Let computer agent handle its own output naturally without F.R.A.N.K.I.E. interference
        response = use_computer_agent("research mode")
        
        # Set global flag to indicate research mode setup is complete (fallback)
        global research_mode_setup_complete
        research_mode_setup_complete = True
        
        return True
        
    except Exception as e:
        # Only show F.R.A.N.K.I.E. error if computer agent also fails
        console.print()
        console.print(Panel(
            f"[danger]Research mode setup failed:[/danger] {str(e)}",
            title="[danger]❌ Setup Failed[/danger]",
            border_style="red",
            box=ROUNDED,
            padding=(1, 2)
        ))
        return False

def route_shortcut_to_computer(shortcut_command):
    """Route a detected shortcut directly to the computer agent"""
    
    if shortcut_command == "research mode":
        # Special multi-step research mode workflow - no F.R.A.N.K.I.E. routing messages
        # Let agents handle their own output naturally
        return handle_research_mode_workflow()
    
    # For non-research shortcuts, show F.R.A.N.K.I.E. routing message
    console.print(f"[highlight]⚡ Auto-routing shortcut:[/highlight] `{shortcut_command}`")
    
    spinner_manager.start_tool_spinner("Computer Agent", f"Executing shortcut: {shortcut_command}")
    
    try:
        start_time = time.time()
        
        # Route directly to computer agent with the shortcut
        response = use_computer_agent(shortcut_command)
        
        duration = time.time() - start_time
        spinner_manager.succeed_tool("Computer Agent", "Shortcut executed", duration)
        
        # Format the response with shortcut context
        console.print()
        console.print(Panel(
            f"[success]⚡ Shortcut Executed:[/success] `{shortcut_command}`\n\n{response}",
            title="[highlight]🚀 Computer Agent Shortcut[/highlight]",
            border_style="magenta",
            box=ROUNDED,
            padding=(1, 2)
        ))
        return True
        
    except Exception as e:
        duration = time.time() - start_time if 'start_time' in locals() else 0
        spinner_manager.fail_tool("Computer Agent", f"Shortcut error: {str(e)}", duration)
        
        console.print()
        console.print(Panel(
            f"[danger]Error executing shortcut:[/danger] `{shortcut_command}`\n[danger]Error:[/danger] {str(e)}\n\n[warning]💡 Try using explicit routing:[/warning]\n• `send computer {shortcut_command}`",
            title="[danger]❌ Shortcut Error[/danger]",
            border_style="red",
            box=ROUNDED
        ))
        return False

def clear_research_mode_state():
    """Clear the research mode state flags"""
    global research_mode_setup_complete, research_mode_active
    research_mode_setup_complete = False
    research_mode_active = False

def handle_post_research_mode_input(user_input):
    """Handle user input after research mode setup is complete - with Quip integration option"""
    global research_mode_setup_complete
    
    # Clear the flag
    research_mode_setup_complete = False
    
    # Route directly to browser agent and capture the research output
    try:
        # Format research query for browser agent
        research_query = f"Research this topic using DuckDuckGo: {user_input}. Provide comprehensive information and key findings. Please avoid creating multiple tabs"
        
        # Route to browser agent for research - let it handle its own output naturally
        research_output = use_browser_agent(research_query)
        
        # After research completes, ask user about Quip documentation
        console.print()
        quip_response = console.input("[highlight]📝 Would you like to document this research in a Quip document? (y/n): [/highlight]").strip().lower()
        
        if quip_response in ['y', 'yes']:
            # User wants Quip documentation - set up Quip and type the research
            console.print()
            console.print("[highlight]📝 Setting up Quip document for research documentation...[/highlight]")
            
            # Step 1: Set up Quip for research
            setup_response = use_computer_agent("setup_quip_for_research")
            
            # Step 2: Send research output to computer agent to type up in Quip
            typing_instructions = f"""You should use the content that the browser agent found to type a paper about the topic in the open new Quip document
            
Format it professionally with proper headings, bullet points, and structure. The current view is the left half of the screen is quip, and the right half is the terminal where you are running, click on the left side to type into the quip. Click repeatedly on Untitled then type your title, then type the document. Here is the research content to use in your paper:

{research_output}

Please type this research content into the Quip document that should now be open."""
            
            computer_typing_response = use_computer_agent(typing_instructions)
            
            console.print()
            console.print(Panel(
                "[bold green]✅ Research Documentation Complete![/bold green]\n\n"
                "✅ Research completed successfully\n"
                "✅ Quip document set up and opened\n"
                "✅ Research findings typed into Quip document\n\n"
                "[bold cyan]Your research is now documented and ready for sharing![/bold cyan]",
                title="[highlight]📋 Research & Documentation Complete[/highlight]",
                border_style="green",
                box=ROUNDED,
                padding=(1, 2)
            ))
            
        elif quip_response in ['n', 'no']:
            # User doesn't want Quip documentation - research flow stops here
            console.print()
            console.print(Panel(
                "[bold green]✅ Research Complete![/bold green]\n\n"
                "[bold cyan]Research findings have been provided above.[/bold cyan]\n"
                "[bold yellow]Research mode ended as requested - no documentation created.[/bold yellow]",
                title="[highlight]🔬 Research Complete[/highlight]",
                border_style="blue",
                box=ROUNDED,
                padding=(1, 2)
            ))
        else:
            # Invalid response - default to no documentation
            console.print()
            console.print(Panel(
                "[bold yellow]⚠️ Invalid response - defaulting to no documentation[/bold yellow]\n\n"
                "[bold green]✅ Research Complete![/bold green]\n"
                "[bold cyan]Research findings have been provided above.[/bold cyan]",
                title="[highlight]🔬 Research Complete[/highlight]",
                border_style="yellow",
                box=ROUNDED,
                padding=(1, 2)
            ))
        
        return True
        
    except Exception as e:
        # Only show F.R.A.N.K.I.E. error handling if the browser agent fails
        console.print()
        console.print(Panel(
            f"[danger]Error researching topic:[/danger] `{user_input}`\n[danger]Error:[/danger] {str(e)}\n\n"
            "[warning]💡 Falling back to normal orchestrator routing...[/warning]",
            title="[danger]❌ Research Error[/danger]",
            border_style="red",
            box=ROUNDED,
            padding=(1, 2)
        ))
        return False

def render_goodbye_message():
    """Premium goodbye message"""
    goodbye_panel = Panel(
        Align.center("[highlight]Thank you for using F.R.A.N.K.I.E.![/highlight]\n[system]Intelligent Multi-Agent Productivity System[/system]"),
        title="[success]👋 Goodbye[/success]",
        border_style="blue",
        box=ROUNDED,
        padding=(1, 2)
    )
    console.print()
    console.print(goodbye_panel)
    console.print()

# Enhanced system prompt for orchestrator
ORCHESTRATOR_SYSTEM_PROMPT = """
You are F.R.A.N.K.I.E. (Flexible Responsive Agent for Navigation Knowledge Integration and Execution), 
an intelligent multi-agent orchestration system that coordinates specialized AI agents to handle complex user requests.

CORE FUNCTIONALITY:
You serve as the central intelligence that analyzes incoming user requests, determines the most appropriate 
specialist agent, and routes tasks for optimal results. Your role is critical in providing seamless, 
intelligent assistance while maintaining premium user experience.

SYSTEM ARCHITECTURE:
- You are the Orchestrator Agent with premium CLI interface integration
- You coordinate 5 specialized agents, each with unique capabilities and tools
- You provide unified responses while leveraging distributed agent expertise
- You maintain context awareness across multi-step workflows with real-time feedback

INTELLIGENT ROUTING RULES:
🌐 Browser Agent (use_browser_agent):
   - Web browsing, site automation, web scraping, HTML parsing
   - Online research, data extraction, web form automation
   - Website interaction, link following, content retrieval

🧠 MEMORY MANAGEMENT (Hybrid Approach):

🧠 DIRECT MEMORY ACCESS (use retrieve tool directly):
   - Quick information retrieval and knowledge searches
   - Simple context lookups during conversations
   - User preference checks and basic knowledge queries
   - Fast memory integration into any response
   - Examples: "What did you tell me about X?", "Do you remember my preferences?", "Retrieve information about Y"

🧠 Memory Brain Agent (use_memory_brain_agent):
   - Complex file processing and format conversions (PDF, DOCX, images, audio)
   - Advanced AWS Bedrock knowledge base management and diagnostics
   - Complex memory organization and categorization tasks
   - Bulk operations and system-level memory management
   - Examples: "Process this document and store it", "Organize my knowledge base", "Convert this file to markdown"

👨‍💻 Coding Agent (coding_agent):
   - All software development tasks: writing, reviewing, refactoring code
   - Programming help across all languages and frameworks
   - Code analysis, debugging, optimization, best practices
   - Architecture design, testing strategies, documentation
   - **TERMINAL & FILE OPERATIONS**: Any request involving terminal commands, file examination, directory navigation
   - File system exploration, looking at file contents, terminal-based operations
   - Examples: "Write a function", "Review this code", "Fix this bug", "Look at the files in this directory", "Check what's in that log file", "Show me the contents of config.json"

✍️ Content Generator Agent (content_generator_agent):
   - UML diagram creation (class, sequence, activity diagrams)
   - AWS architecture visualization and cloud diagrams
   - System design diagrams, flowcharts, process maps
   - Document generation, content creation, and visual assets

💻 Computer Agent (use_computer_agent):
   - Desktop automation and control with direct access
   - Screenshot capture, application launching
   - File system operations, system interactions

PREMIUM UX GUIDELINES:
1. Always provide clear agent routing explanations with professional formatting
2. Use appropriate emojis and styling for visual hierarchy  
3. Maintain helpful, efficient, and user-focused communication
4. Provide context about agent capabilities relevant to the request
5. Format responses with proper structure for premium experience
6. When uncertain, ask clarifying questions to ensure proper routing

Your goal is to provide intelligent, efficient coordination of specialized AI capabilities 
to maximize user productivity with premium interface experience.
"""

# Create orchestrator agent
orchestrator_agent = Agent(
    name="orchestrator_agent",
    system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
    tools=[rss, use_browser_agent, mcp_client, content_generator_agent, current_time, coding_agent, 
           use_computer_agent, use_memory_brain_agent, retrieve, slack],
)

def main():
    """Premium main execution with enhanced CLI"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="F.R.A.N.K.I.E. - Premium Multi-Agent Productivity System"
    )
    parser.add_argument("query", nargs="*", help="Query to process directly")
    parser.add_argument("--agent", help="Route directly to specific agent")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Setup environment
    os.environ["STRANDS_RSS_STORAGE_PATH"] = os.path.join(os.getcwd(), "rss_feeds", "news")
    os.makedirs(os.environ["STRANDS_RSS_STORAGE_PATH"], exist_ok=True)
    
    try:
        # Clear screen for premium experience
        console.clear()
        
        # Process direct query or enter interactive mode
        if args.query:
            query = " ".join(args.query)
            spinner_manager.start_thinking("Processing query with specialized agent...")
            
            try:
                response = orchestrator_agent(query)
                spinner_manager.stop()
                format_premium_response(response)
            except Exception as e:
                spinner_manager.stop()
                console.print(f"[danger]Error: {str(e)}[/danger]")
            return
        
        # Interactive mode
        render_premium_welcome()
        console.print("[prompt]🎯 F.R.A.N.K.I.E. is ready for your requests![/prompt]")
        
        while True:
            try:
                # Enhanced prompt
                console.print()
                user_input = console.input("[prompt]🎯 F.R.A.N.K.I.E. > [/prompt]").strip()
                
                # Handle special commands
                if user_input.lower() in ["exit", "quit", "bye"]:
                    clear_research_mode_state()
                    render_goodbye_message()
                    break
                    
                elif user_input.lower() in ["help", "?"]:
                    clear_research_mode_state()
                    show_premium_help()
                    continue
                    
                elif user_input.lower() in ["shortcuts", "show_shortcuts", "computer_shortcuts", "quick_actions"]:
                    clear_research_mode_state()
                    show_shortcuts_menu()
                    continue
                    
                elif user_input.lower() == "clear":
                    clear_research_mode_state()
                    console.clear()
                    render_premium_welcome()
                    continue
                    
                elif user_input.startswith("!"):
                    clear_research_mode_state()
                    # Shell command
                    shell_cmd = user_input[1:].strip()
                    if shell_cmd:
                        handle_shell_command(shell_cmd)
                    continue
                    
                elif not user_input:
                    console.print("[warning]💭 Please enter a command or request. Type 'help' for guidance.[/warning]")
                    continue
                
                # Check if we're in post-research-mode state
                global research_mode_setup_complete
                if research_mode_setup_complete:
                    if handle_post_research_mode_input(user_input):
                        continue
                    # If research handling failed, fall through to normal processing
                
                # Check for computer shortcuts first (before orchestrator)
                detected_shortcut = detect_shortcut(user_input)
                if detected_shortcut:
                    # Route to computer agent (routing message logic handled in route_shortcut_to_computer)
                    if route_shortcut_to_computer(detected_shortcut):
                        continue
                    # If shortcut routing failed, fall through to orchestrator
                
                # Process regular requests
                spinner_manager.start_thinking("Processing request with specialized agent...")
                
                try:
                    response = orchestrator_agent(user_input)
                    spinner_manager.stop()
                    format_premium_response(response)
                    
                except Exception as e:
                    spinner_manager.stop()
                    console.print()
                    console.print(Panel(
                        f"[danger]Error Type:[/danger] {type(e).__name__}\n[danger]Message:[/danger] {str(e)}\n\n[warning]💡 Troubleshooting:[/warning]\n• Try rephrasing your request\n• Use 'help' for available commands\n• Check system status",
                        title="[danger]❌ System Error[/danger]",
                        border_style="red",
                        box=ROUNDED
                    ))
                    
            except KeyboardInterrupt:
                spinner_manager.stop()
                console.print(f"\n[warning]⚠️ Interrupt detected[/warning]")
                
                try:
                    confirm = console.input("[warning]Exit F.R.A.N.K.I.E.? (y/N): [/warning]").lower()
                    if confirm in ['y', 'yes']:
                        render_goodbye_message()
                        break
                    else:
                        console.print("[success]✅ Resuming session...[/success]")
                        continue
                except (KeyboardInterrupt, EOFError):
                    render_goodbye_message()
                    break
                    
            except EOFError:
                render_goodbye_message()
                break
                
    except Exception as e:
        spinner_manager.stop()
        console.print()
        console.print(Panel(
            f"[danger]Critical Error:[/danger] {str(e)}\n[system]System will exit safely...[/system]",
            title="[danger]💥 Critical System Error[/danger]",
            border_style="red",
            box=ROUNDED
        ))
        sys.exit(1)

if __name__ == "__main__":
    main()