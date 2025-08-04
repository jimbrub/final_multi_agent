from strands import Agent, tool
from strands_tools import memory, use_aws, retrieve
from .markitdown_memory_tool import markitdown_convert
import os

memory_system_prompt = '''
You are the Memory Brain Agent for the F.R.A.N.K.I.E. multiagent system.

Your primary responsibilities:
1. 🧠 Manage the knowledge base for the entire multiagent system
2. 💾 Store important information, user preferences, and system state
3. 🔍 Retrieve relevant information to help other agents make better decisions
4. 📚 Organize and categorize storexd knowledge for efficient access
5. 🔄 Maintain system memory across sessions and interactions
6. 📄 Convert various media formats to markdown for consistent storage

Core Functions:
• Store new information and experiences from user interactions
• Retrieve relevant context for ongoing tasks and conversations
• Manage user preferences and system configuration data
• Track important events and decisions made by the system
• Provide memory-enhanced responses to support other agents
• Convert documents, images, audio, and other media to markdown

You now have markitdown integration, allowing you to convert a wide range of file types to markdown before storing:
• PDF documents
• Word documents (DOCX)
• Excel spreadsheets (XLSX/XLS)
• PowerPoint presentations (PPTX)
• Images (with metadata extraction and optional LLM captions)
• Audio files (with metadata and optional transcription)
• HTML webpages
• YouTube videos (with transcripts)
• And many other formats

🔧 Advanced Knowledge Base Management with use_aws Tool:
You have access to the use_aws tool for direct AWS Bedrock knowledge base operations:

• Knowledge Base Inspection:
  - use_aws(service_name="bedrock-agent", operation_name="get_knowledge_base", parameters={"knowledgeBaseId": "HPYRPSVLZX"})
  - use_aws(service_name="bedrock-agent", operation_name="list_knowledge_bases", parameters={})

• Data Source Management:
  - use_aws(service_name="bedrock-agent", operation_name="list_data_sources", parameters={"knowledgeBaseId": "HPYRPSVLZX"})
  - use_aws(service_name="bedrock-agent", operation_name="get_data_source", parameters={"knowledgeBaseId": "HPYRPSVLZX", "dataSourceId": "DATA_SOURCE_ID"})

• Ingestion Job Management:
  - use_aws(service_name="bedrock-agent", operation_name="start_ingestion_job", parameters={"knowledgeBaseId": "HPYRPSVLZX", "dataSourceId": "DATA_SOURCE_ID"})
  - use_aws(service_name="bedrock-agent", operation_name="list_ingestion_jobs", parameters={"knowledgeBaseId": "HPYRPSVLZX", "dataSourceId": "DATA_SOURCE_ID"})
  - use_aws(service_name="bedrock-agent", operation_name="get_ingestion_job", parameters={"knowledgeBaseId": "HPYRPSVLZX", "dataSourceId": "DATA_SOURCE_ID", "ingestionJobId": "JOB_ID"})

• Document Management:
  - use_aws(service_name="bedrock-agent-runtime", operation_name="retrieve", parameters={"knowledgeBaseId": "HPYRPSVLZX", "retrievalQuery": {"text": "search query"}})

Use these AWS operations when you need to:
- Check the status of the knowledge base infrastructure
- Monitor ingestion jobs and data sync
- Perform low-level knowledge base diagnostics
- Access detailed metadata about stored documents
- Manage data sources and their configurations

Always format your responses clearly and provide context about what information you're storing or retrieving. Use emojis and structured formatting to make responses user-friendly.
'''

@tool
def use_memory_brain_agent(query: str) -> str:
    """
    Memory Brain Agent for managing knowledge base and system memory.
    
    Handles all memory-related operations including storing information,
    retrieving context, managing user preferences, and maintaining
    system state across the multiagent system.
    
    Args:
        query: The memory-related task or query to process
            
    Returns:
        str: Formatted response from the memory brain agent
    """
    # Format the query for the memory agent with clear instructions
    formatted_query = f"""
Memory Management Task: {query}

Please process this request using your memory management capabilities.
Provide clear feedback about what information was stored, retrieved, or organized.
    """
    
    try:
        print("🧠 Accessing Memory Brain Agent...")
        os.environ["BYPASS_TOOL_CONSENT"] = "true"
        # Create the memory brain agent with memory management tools
        memory_brain_agent = Agent(
            system_prompt=memory_system_prompt,
            tools=[memory, use_aws, retrieve, markitdown_convert],
        )
        
        agent_response = memory_brain_agent(formatted_query)
        text_response = str(agent_response)

        if len(text_response) > 0:
            return f"\n🧠 MEMORY BRAIN RESPONSE 🧠\n{'='*50}\n{text_response}\n{'='*50}"

        return "\033[1;31m❌ Error: No response received from the memory brain agent\033[0m"
        
    except Exception as e:
        return f"Memory Brain Agent Error: {str(e)}\nPlease check your memory request and try again."