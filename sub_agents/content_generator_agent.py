#!/usr/bin/env python3
"""
🎨 Content Generator Agent - Visual Content Creation System
==========================================================

SYSTEM OVERVIEW:
The Content Generator Agent is a specialized AI assistant that creates visual content
including diagrams, images, and other visual assets. It leverages two powerful tools
to handle diverse content generation requirements.

CORE CAPABILITIES:
1. **Diagram Creation**: UML diagrams, AWS architectures, flowcharts, and technical diagrams
2. **Image Generation**: Custom images, illustrations, visual assets, and creative content

TOOLS AVAILABLE:
- diagram: Creates technical diagrams using various diagramming standards
- generate_image: Generates custom images from text descriptions using AI

ARCHITECTURE:
Built on the Strands Agent framework with Claude 3.7 Sonnet model for high-quality
content generation and visual understanding.
"""

import os
from strands import tool
from botocore.config import Config
from strands import Agent
from strands.models import BedrockModel
from strands_tools import diagram, generate_image


system_prompt = """
You are a Content Generator Agent specializing in visual content creation. You have access to two powerful tools:

1. **Diagram Tool**: Create technical diagrams including:
   - All 14 UML diagram types (Class, Use Case, Sequence, Activity, etc.)
   - AWS cloud architecture diagrams
   - System design diagrams, flowcharts, and process maps
   - Network topology diagrams

2. **Generate Image Tool**: Create custom images including:
   - Illustrations and artwork
   - Visual assets and graphics
   - Custom images from text descriptions
   - Creative visual content

Your role is to analyze requests and determine whether they need diagram creation or image generation,
then use the appropriate tool to deliver high-quality visual content that meets the user's specifications.

Always provide clear explanations of your process and the visual content you're creating.
"""


# Initialize the Strands Agent with Computer Use capabilities and speech


@tool
def content_generator_agent(query: str) -> str:
    """
    Content Generator Agent that creates visual content including diagrams and images.
    
    This agent has access to two specialized tools:
    
    1. **DIAGRAM TOOL** - Creates technical diagrams:
       - UML Diagrams (all 14 types):
         * Class, Use Case, Sequence, Activity Diagrams
         * State Machine, Component, Deployment Diagrams
         * Object, Package, Communication Diagrams
         * Timing, Interaction Overview, Profile Diagrams
         * Composite Structure Diagrams
       
       - AWS Cloud Architecture Diagrams:
         * Infrastructure diagrams, Service architectures
         * Network topology, Security architectures
         * Multi-region deployments, Microservices diagrams
    
    2. **IMAGE GENERATION TOOL** - Creates custom images:
       - Illustrations and artwork
       - Visual assets and graphics
       - Custom images from detailed text descriptions
       - Creative visual content and concepts
        
    Args:
        query (str): User's request for creating visual content. Should include:
            - Type of content needed (diagram vs image)
            - Specific requirements and details
            - Key elements/components to include
            - Any styling, format, or layout preferences
    
    Returns:
        str: Response containing:
            - The completed visual content or file path
            - Progress updates during creation process
            - Technical details about the generated content
            - Error messages if the request couldn't be completed
    
    Examples:
        # Diagram requests
        query: "Create a class diagram for a library management system"
        query: "Build an AWS architecture diagram for a web application"
        
        # Image requests  
        query: "Generate an image of a futuristic city skyline"
        query: "Create an illustration of a data flow process"
    """
    # Format the query for the content generator with clear instructions
    formatted_query = f"""
    Please help me create the following visual content. I will:
    1. Analyze the content requirements and determine the appropriate tool
    2. For diagrams: Ensure proper element relationships, connections, and standard notation
    3. For images: Create detailed, high-quality visual content based on specifications
    4. Provide clear progress updates during creation
    5. Validate the final output meets requirements and quality standards

    Content Request: {query}
    """
    
    try:
        print("🎨 Initiating Content Generation Process")
        # Create the content generator agent with both tools
        content_agent = Agent(
            system_prompt=system_prompt,
            tools=[diagram, generate_image],
        )
        agent_response = content_agent(formatted_query)
        text_response = str(agent_response)

        if len(text_response) > 0:
            return f"\n🎨 CONTENT GENERATOR RESPONSE 🎨\n{'='*50}\n{text_response}\n{'='*50}"

        return "\033[1;31m❌ Error: No content output received from the generation process\033[0m"
    except Exception as e:
        # Return specific error message for content generation processing
        return f"Content Generation Error: {str(e)}\nPlease verify your content requirements and try again."
    
if __name__ == "__main__":
    print(f"\n\033[1;36m🎨 Content Generator Agent 🎨\033[0m\n")
    print("🚀 Visual Content Creation System")
    print("Available capabilities:")
    print("  📊 Technical Diagrams: UML, AWS architectures, flowcharts, system designs")
    print("  🖼️  Custom Images: Illustrations, artwork, visual assets, creative content")
    print("  💬 Interactive Mode: Type your content request below")
    print("  🚪 Exit: Type 'exit' to quit")
    print("")

    # Create a direct instance for interactive use
    interactive_agent = Agent(system_prompt=system_prompt, tools=[diagram, generate_image])

    while True:
        user_input = input("\n\033[1;33m🎨 Content Request > \033[0m")  # Yellow prompt with emoji
        
        if user_input.lower() == "exit":
            print("\n\033[1;36m👋 Thanks for using Content Generator Agent! Goodbye!\033[0m")
            break
            
        # Use ANSI color codes to make the agent's response stand out
        print("\n\033[1;36m--- 🎨 Content Generator Response ---\033[0m")  # Cyan color, bold text
        interactive_agent(user_input)
        print("\033[1;36m--- ✅ Content Generation Complete ---\033[0m\n")  # Cyan color, bold text