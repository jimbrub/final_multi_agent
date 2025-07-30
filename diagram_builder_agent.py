#!/usr/bin/env python3
import os
import sys
import logging
import argparse
from strands import tool
from botocore.config import Config
from strands import Agent
from strands.models import BedrockModel
from strands_tools import http_request, speak, diagram
# import diagram 
import sys
import os


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
you are an agent that assists in building diagrams
you can build any of the 14 uml diagrams
you can build AWS cloud architecture diagrams
"""


# Initialize the Strands Agent with Computer Use capabilities and speech


@tool
def diagram_builder_agent(query: str) -> str:
    """
    Creates and modifies various types of diagrams based on user requirements.
    
    Supports:
    - UML Diagrams (all 14 types):
        * Class Diagrams
        * Use Case Diagrams
        * Sequence Diagrams
        * Activity Diagrams
        * State Machine Diagrams
        * Component Diagrams
        * Deployment Diagrams
        * Object Diagrams
        * Package Diagrams
        * Communication Diagrams
        * Timing Diagrams
        * Interaction Overview Diagrams
        * Profile Diagrams
        * Composite Structure Diagrams
    
    - AWS Cloud Architecture Diagrams:
        * Infrastructure Diagrams
        * Service Architecture
        * Network Topology
        * Security Architectures
        
    Args:
        query (str): User's request for creating or modifying a diagram. Should include:
            - Type of diagram needed
            - Key elements/components to include
            - Any specific styling or layout preferences
            - Modifications needed for existing diagrams
    
    Returns:
        str: Response containing either:
            - The completed diagram in the specified format
            - Progress updates during diagram creation
            - Error messages if the request couldn't be completed
    
    Example:
        query: "Create a class diagram for a library management system with Book, 
               User, and Librarian classes" 
    """
    # Format the query for the math agent with clear instructions
    formatted_query = f"""
    Please help me create/modify the following diagram. I will:
    1. Analyze the diagram requirements and type
    2. Ensure proper element relationships and connections
    3. Follow standard notation and conventions
    4. Provide clear progress updates during creation
    5. Validate the final diagram against standard specifications

    Diagram Request: {query}
    """
    
    try:
        print("Initiating Diagram Creation Process")
        # Create the math agent with calculator capability
        diagram_agent = Agent(
            system_prompt=system_prompt,
            model=model,
            tools=[diagram],
        )
        agent_response = diagram_agent(formatted_query)
        text_response = str(agent_response)

        if len(text_response) > 0:
            return f"\n📊 DIAGRAM BUILDER RESPONSE 📊\n{'='*50}\n{text_response}\n{'='*50}"

        return "\033[1;31m❌ Error: No diagram output received from the creation process\033[0m"
    except Exception as e:
        # Return specific error message for math processing
        return f"Diagram Creation Error: {str(e)}\nPlease verify your diagram requirements and try again."