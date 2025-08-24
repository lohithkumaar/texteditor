"""
Utility functions for the Text Tools app.
"""

import streamlit as st
import re
import json
from typing import Any, Optional
from src.config import Config

def sanitize_text(text: str, max_length: int = 1000) -> str:
    """
    Sanitize text input to prevent XSS and limit length.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text string
    """
    if not isinstance(text, str):
        return str(text)[:max_length]
    
    # Remove potential HTML/script tags
    sanitized = re.sub(r'<[^>]*>', '', text)
    
    # Limit length
    return sanitized[:max_length]

def init_session_state() -> None:
    """Initialize Streamlit session state with default values."""
    # Updated session keys for general text editing
    session_keys = {
        'original_text': '',
        'edited_text': '',
        'validator_text': '',  # Separate text for validator
        'json_schema': '',
        'use_schema': False,
        'mode': 'Editor',
        'file_type': 'json',  # Track file type (json, txt, md)
        'undo_stack': [],
        'show_download': False  # Track download interface visibility
    }
    
    for key, default_value in session_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def add_to_undo_stack(content: str) -> None:
    """
    Add content to the undo stack.
    
    Args:
        content: Content to add to undo stack
    """
    if 'undo_stack' not in st.session_state:
        st.session_state.undo_stack = []
    
    # Don't add if it's the same as the current top
    if (st.session_state.undo_stack and 
        st.session_state.undo_stack[-1] == content):
        return
    
    st.session_state.undo_stack.append(content)
    
    # Limit stack size
    if len(st.session_state.undo_stack) > Config.MAX_UNDO_STACK_SIZE:
        st.session_state.undo_stack.pop(0)

def safe_json_key(key: Any) -> str:
    """
    Safely convert a JSON key to string for display.
    
    Args:
        key: JSON key to convert
    
    Returns:
        Safe string representation of the key
    """
    if isinstance(key, str):
        return sanitize_text(key, 100)
    return str(key)[:100]

def truncate_long_value(value: Any, max_length: int = 200) -> str:
    """
    Truncate long values for display.
    
    Args:
        value: Value to potentially truncate
        max_length: Maximum display length
    
    Returns:
        Truncated string representation
    """
    str_value = str(value)
    if len(str_value) <= max_length:
        return str_value
    return str_value[:max_length] + "..."

def get_json_type_icon(value: Any) -> str:
    """
    Get an appropriate icon for a JSON value type.
    
    Args:
        value: JSON value
    
    Returns:
        Icon string for the value type
    """
    if isinstance(value, dict):
        return "📁"
    elif isinstance(value, list):
        return "📋"
    elif isinstance(value, str):
        return "📝"
    elif isinstance(value, (int, float)):
        return "🔢"
    elif isinstance(value, bool):
        return "☑️" if value else "☐"
    elif value is None:
        return "∅"
    else:
        return "❓"

def get_file_type_icon(file_type: str) -> str:
    """
    Get an appropriate icon for a file type.
    
    Args:
        file_type: File extension/type
    
    Returns:
        Icon string for the file type
    """
    icons = {
        'json': '📋',
        'txt': '📄',
        'md': '📝',
        'markdown': '📝'
    }
    return icons.get(file_type.lower(), '📄')

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def is_large_file(content: str) -> bool:
    """
    Check if content is considered large.
    
    Args:
        content: Text content to check
    
    Returns:
        True if content is large
    """
    return len(content.encode('utf-8')) > Config.MAX_FILE_SIZE_BYTES

def detect_file_type(content: str, filename: str = None) -> str:
    """
    Detect file type based on content and filename.
    
    Args:
        content: File content
        filename: Optional filename
    
    Returns:
        Detected file type (json, txt, md)
    """
    # Check filename extension first
    if filename:
        ext = filename.split('.')[-1].lower()
        if ext in ['json', 'txt', 'md', 'markdown']:
            return 'md' if ext == 'markdown' else ext
    
    # Try to detect from content
    if not content or not content.strip():
        return 'txt'
        
    content = content.strip()
    
    # Check if it's JSON - more robust detection
    if content.startswith(('{', '[')):
        try:
            json.loads(content)
            return 'json'
        except:
            pass
    
    # Check if it's Markdown - look for common markdown patterns
    markdown_patterns = [
        r'^#{1,6}\s',  # Headers
        r'^\*\s',      # Unordered lists
        r'^\d+\.\s',   # Ordered lists
        r'^\-\s',      # Unordered lists with dash
        r'\[.*\]\(.*\)', # Links
        r'\*\*.*\*\*', # Bold
        r'\_\_.*\_\_', # Bold
        r'\*.*\*',     # Italic
        r'\_.*\_',     # Italic
        r'^>',         # Blockquotes
        r'```',        # Code blocks
        r'`.*`'        # Inline code
    ]
    
    # Check multiple lines for markdown patterns
    lines = content.split('\n')
    markdown_score = 0
    
    for line in lines[:10]:  # Check first 10 lines
        for pattern in markdown_patterns:
            if re.search(pattern, line, re.MULTILINE):
                markdown_score += 1
                break
    
    # If we found markdown patterns in more than 20% of checked lines, it's probably markdown
    if markdown_score > len(lines[:10]) * 0.2:
        return 'md'
    
    # Default to txt
    return 'txt'

def count_words(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Text to count words in
    
    Returns:
        Number of words
    """
    if not text:
        return 0
    return len(text.split())

def count_lines(text: str) -> int:
    """
    Count lines in text.
    
    Args:
        text: Text to count lines in
    
    Returns:
        Number of lines
    """
    if not text:
        return 0
    return len(text.splitlines())

def count_paragraphs(text: str) -> int:
    """
    Count paragraphs in text.
    
    Args:
        text: Text to count paragraphs in
    
    Returns:
        Number of paragraphs
    """
    if not text:
        return 0
    return len([p for p in text.split('\n\n') if p.strip()])

def get_text_stats(text: str) -> dict:
    """
    Get comprehensive text statistics.
    
    Args:
        text: Text to analyze
    
    Returns:
        Dictionary with text statistics
    """
    if not text:
        return {
            'characters': 0,
            'words': 0,
            'lines': 0,
            'paragraphs': 0,
            'bytes': 0,
            'kb': 0.0
        }
    
    bytes_count = len(text.encode('utf-8'))
    
    return {
        'characters': len(text),
        'words': count_words(text),
        'lines': count_lines(text),
        'paragraphs': count_paragraphs(text),
        'bytes': bytes_count,
        'kb': bytes_count / 1024
    }