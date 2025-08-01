#!/usr/bin/env python3
"""
Coding Buddy Agent for FRANKIE Multiagent System
Specialized in software engineering, code quality, and production-ready implementations.

This uses interleaved thinking sonnet 4 for better understanding coding principles
"""

import os
from botocore.config import Config
from strands import Agent, tool
from strands.models import BedrockModel
from strands_tools import editor, shell, load_tool, http_request, python_repl, file_read, file_write
os.environ["DEV"] = "true"
os.environ["STRANDS_TOOL_CONSOLE_MODE"] = "enabled"

def create_coding_agent():
    """Create and return the Coding Agent with specialized configuration."""
    
    model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-4-20250514-v1:0", # max 65536 ---> suggested
        max_tokens=10000,
        boto_client_config=Config(
            read_timeout=900,
            connect_timeout=900,
            retries=dict(max_attempts=3, mode="adaptive"),
        ),
        additional_request_fields={
            "anthropic_beta": ["interleaved-thinking-2025-05-14"],
            "thinking": {
                "type": os.getenv("STRANDS_THINKING_TYPE", "enabled"),
                "budget_tokens": int(os.getenv("STRANDS_BUDGET_TOKENS", "2048")),
            },
        },
    )

    system_prompt = """
You are an expert software engineering assistant focused on producing high-quality, production-ready code. You combine technical expertise with practical software engineering principles to deliver optimal solutions.

CORE COMPETENCIES:
1. Code Quality
- Apply SOLID principles and design patterns
- Ensure clean, maintainable, and self-documenting code
- Identify and refactor code smells
- Optimize code structure and organization
- Balance pragmatic solutions with best practices

2. Production Engineering
- Implement robust error handling and logging
- Design comprehensive testing strategies
- Integrate security best practices
- Consider deployment and scaling requirements
- Ensure proper monitoring and observability
- Implement appropriate configuration management

3. Performance Optimization
- Identify and resolve bottlenecks
- Optimize resource utilization
- Implement effective caching strategies
- Address concurrency and threading
- Consider scalability implications
- Profile and benchmark code

4. Code Review & Analysis
- Evaluate code quality and structure
- Verify exception handling patterns
- Assess logging and monitoring coverage
- Validate documentation completeness
- Check backward compatibility
- Identify security vulnerabilities

EXECUTION PROTOCOL:
1. Analyze Requirements
- Understand the core problem
- Consider scalability needs
- Identify potential challenges
- Plan appropriate architecture

2. Implementation Approach
- Start with simple, working solutions
- Refactor for clarity and efficiency
- Add necessary safeguards
- Implement testing strategy
- Document key decisions

3. Quality Assurance
- Verify error handling
- Validate edge cases
- Ensure proper testing
- Check performance implications
- Confirm security measures

TOOLS UTILIZATION:
- editor: Code modification
- python_repl: Code execution
- shell: System commands
- file_read/write: File operations
- http_request: API interactions

OUTPUT GUIDELINES:
- Provide clear, documented code
- Include usage examples
- Explain key design decisions
- Highlight potential issues
- Suggest testing approaches
- Note performance considerations

Priority: Maintainable, secure, and efficient code that follows software engineering best practices.
"""

    # Create the agent with specialized tools for coding
    agent = Agent(
        system_prompt=system_prompt,
        model=model,
        tools=[
            editor,
            python_repl,
            shell,
            file_read,
            file_write,
            load_tool,
            http_request
        ]
    )
    
    return agent

@tool
def coding_agent(user_input: str) -> str:
    """
    Specialized coding assistant for software engineering tasks.
    
    Handles code analysis, writing, review, refactoring, and software engineering 
    best practices. Focuses on production-ready, maintainable, and scalable code.
    
    Args:
        user_input: The coding-related request or question
        
    Returns:
        Expert response with code analysis, suggestions, or implementations
    """
    agent = create_coding_agent()
    os.environ["BYPASS_TOOL_CONSENT"] = "true"

    try:
        response = agent(user_input)
        return response
    except Exception as e:
        return f"❌ Coding Agent Error: {str(e)}"

# Test the agent directly if run as main
if __name__ == "__main__":
    
    while True:
        user_input = input("\n\033[1;33m> \033[0m")
        if user_input.lower() == "exit":
            print("\n\033[1;36mHappy coding! 👋\033[0m")
            break
        
        print("\n\033[1;36m--- Coding Agent Response ---\033[0m")
        result = coding_agent(user_input)
        print(result)
        print("\033[1;36m--- End of Response ---\033[0m\n")