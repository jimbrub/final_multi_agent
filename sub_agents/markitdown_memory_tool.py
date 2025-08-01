"""
Markitdown Memory Integration Tool

This tool provides integration between the markitdown package and the memory agent
system to convert various media formats to markdown before storing in the knowledge base.

It handles all the complexity of file conversion, ensuring that media of different formats
can be consistently stored as markdown in the knowledge base.
"""

import os
import io
import tempfile
from typing import Optional, Dict, Any, Union, BinaryIO
from pathlib import Path

from strands import tool
from markitdown import MarkItDown

@tool
def markitdown_convert(
    source: str, 
    llm_client: Optional[Any] = None,
    llm_model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convert various media formats to markdown using markitdown.
    
    This tool converts documents, images, audio files, and other media types
    to markdown format for consistent storage and processing in the knowledge base.
    
    Args:
        source: Path to the file or URL to convert
        llm_client: Optional LLM client for enhanced descriptions (like OpenAI client)
        llm_model: Optional LLM model name (like "gpt-4o")
        
    Returns:
        A dictionary containing the status and the converted markdown content
    """
    try:
        # Initialize the MarkItDown converter with optional LLM enhancement
        md_converter = MarkItDown(
            llm_client=llm_client,
            llm_model=llm_model
        )
        
        # Convert the source to markdown
        result = md_converter.convert(source)
        
        # Return the successful conversion result
        return {
            "status": "success",
            "content": [
                {"text": f"✅ Successfully converted content to markdown"},
                {"text": f"Source: {source}"},
                {"text": f"Content type: {result.content_type if hasattr(result, 'content_type') else 'Unknown'}"},
                {"text": f"Markdown content:\n\n{result.text_content}"}
            ]
        }
    except Exception as e:
        # Return error information in case of conversion failure
        return {
            "status": "error",
            "content": [
                {"text": f"❌ Error converting content to markdown: {str(e)}"}
            ]
        }
