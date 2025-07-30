#!/usr/bin/env python3
import os
import sys
import logging
from typing import Dict, List, Optional, Union
from strands import tool


from botocore.config import Config
from strands import Agent
from strands.models import BedrockModel

from strands_tools import http_request, slack, rss
# import rss

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# Bedrock model with Computer Use capabilities (Claude 3.7 Sonnet)
model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0", 
    # model_id="us.anthropic.claude-opus-4-20250514-v1:0", max_tokens=10000, # max 32768 --> smartest
    # model_id="us.anthropic.claude-sonnet-4-20250514-v1:0", max_tokens=10000, # max 65536 ---> suggested
    # model_id="us.amazon.nova-premier-v1:0", max_tokens=10000, # max 32000
    # model_id="us.amazon.nova-pro-v1:0", max_tokens=10000, # max 10000. # --> fastest
    max_tokens=10000,
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

# Set environment variables
os.environ["DEV"] = "true"
os.environ["STRANDS_TOOL_CONSOLE_MODE"] = "enabled"

system_prompt = """
You are an ambitious news reporter who loves all the breaking news. You are enthusiastic about your job and freedom of speech and information which is why you love using the rss tool to find BREAKING news.

When handling RSS requests:
1. Be proactive about getting the latest news
2. Organize information in a clean, easy-to-read format
3. Highlight important headlines with formatting
4. Provide context and summary for news items when appropriate
5. Help users stay informed about topics they care about

For RSS feed management:
- Subscribe to relevant news sources
- Update feeds regularly
- Search for specific topics across feeds
- Display content in a readable format
"""


# Initialize the Strands Agent with Computer Use capabilities
agent = Agent(system_prompt=system_prompt, model=model, tools=[http_request, rss])

@tool
def news_reporter_agent(query: str) -> str:
    """
    Process and respond to news and RSS-related queries using the specialized news reporter agent.
    
    This tool allows the productivity orchestrator to delegate any RSS-related tasks to the news reporter,
    including subscribing to feeds, updating feeds, searching for news, and reading news content.
    
    Args:
        query: A news-related query or RSS management command from the user
        
    Returns:
        A formatted response containing news information or confirmation of RSS actions
    """
    try:
        print("\033[90m[Routing query to News Reporter Agent]\033[0m")
        
        # Format the output with news reporter styling
        formatted_query = f"Process this news or RSS request: {query}"
        
        agent_response = agent(formatted_query)
        text_response = str(agent_response)

        if len(text_response) > 0:
            return f"\n📰 NEWS REPORTER RESPONSE 📰\n{'='*50}\n{text_response}\n{'='*50}"

        return "\033[1;31m❌ I apologize, but I couldn't process your news-related request. Please check if your query is clear or try rephrasing it.\033[0m"
    except Exception as e:
        # Return specific error message for news processing
        return f"Error processing your news request: {str(e)}"