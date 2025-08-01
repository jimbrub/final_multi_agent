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

### 💡 **Quick Start**
- Use natural language for any request - F.R.A.N.K.I.E. will route it optimally
- Type `help` for complete command reference and examples
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

### 🎯 **Best Practices**  
- Be specific about desired outcomes for better agent selection
- Use the memory agent to store important preferences and context
- Combine agents for complex tasks (e.g., "Research topic X and create a diagram")
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
        # Import here to avoid circular imports
        from strands_tools import shell
        
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
                    render_goodbye_message()
                    break
                    
                elif user_input.lower() in ["help", "?"]:
                    show_premium_help()
                    continue
                    
                elif user_input.lower() == "clear":
                    console.clear()
                    render_premium_welcome()
                    continue
                    
                elif user_input.startswith("!"):
                    # Shell command
                    shell_cmd = user_input[1:].strip()
                    if shell_cmd:
                        handle_shell_command(shell_cmd)
                    continue
                    
                elif not user_input:
                    console.print("[warning]💭 Please enter a command or request. Type 'help' for guidance.[/warning]")
                    continue
                
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