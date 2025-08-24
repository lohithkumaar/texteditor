"""
JSON formatting and minification functions for Text Tools.
"""

import json
from typing import Any, Optional

def format_json(
    json_text: str,
    indent: int = 2,
    sort_keys: bool = False,
    ensure_ascii: bool = False
) -> str:
    """
    Format JSON with specified indentation and options.
    
    Args:
        json_text: JSON string to format
        indent: Number of spaces for indentation
        sort_keys: Whether to sort object keys
        ensure_ascii: Whether to escape non-ASCII characters
    
    Returns:
        Formatted JSON string
    
    Raises:
        json.JSONDecodeError: If input is not valid JSON
        ValueError: If formatting fails
    """
    if not json_text.strip():
        raise ValueError("Empty JSON input")
    
    try:
        # Parse JSON
        parsed_data = json.loads(json_text)
        
        # Format with specified options
        formatted = json.dumps(
            parsed_data,
            indent=indent if indent > 0 else None,
            sort_keys=sort_keys,
            ensure_ascii=ensure_ascii,
            separators=(',', ': ') if indent > 0 else (',', ':')
        )
        
        return formatted
        
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON: {e.msg}", e.doc, e.pos)
    except Exception as e:
        raise ValueError(f"Formatting failed: {str(e)}")

def minify_json(json_text: str, ensure_ascii: bool = False) -> str:
    """
    Minify JSON by removing all unnecessary whitespace.
    
    Args:
        json_text: JSON string to minify
        ensure_ascii: Whether to escape non-ASCII characters
    
    Returns:
        Minified JSON string
    
    Raises:
        json.JSONDecodeError: If input is not valid JSON
    """
    return format_json(json_text, indent=0, sort_keys=False, ensure_ascii=ensure_ascii)

def pretty_format_json(
    json_text: str,
    indent: int = 2,
    sort_keys: bool = True
) -> str:
    """
    Format JSON with pretty printing options optimized for readability.
    
    Args:
        json_text: JSON string to format
        indent: Number of spaces for indentation
        sort_keys: Whether to sort object keys
    
    Returns:
        Pretty formatted JSON string
    """
    return format_json(json_text, indent=indent, sort_keys=sort_keys, ensure_ascii=False)

def compact_format_json(json_text: str, max_line_length: int = 80) -> str:
    """
    Format JSON in a compact style that balances readability and space.
    
    Args:
        json_text: JSON string to format
        max_line_length: Target maximum line length
    
    Returns:
        Compact formatted JSON string
    """
    try:
        parsed_data = json.loads(json_text)
        
        # Use minimal indentation for compact format
        formatted = json.dumps(
            parsed_data,
            indent=1,
            sort_keys=False,
            ensure_ascii=False,
            separators=(',', ': ')
        )
        
        return formatted
        
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON: {e.msg}", e.doc, e.pos)

def sort_json_keys(json_text: str, indent: int = 2) -> str:
    """
    Sort all JSON object keys recursively.
    
    Args:
        json_text: JSON string to process
        indent: Indentation for output
    
    Returns:
        JSON with sorted keys
    """
    return format_json(json_text, indent=indent, sort_keys=True)

def normalize_json(json_text: str) -> str:
    """
    Normalize JSON by parsing and re-serializing with standard formatting.
    
    Args:
        json_text: JSON string to normalize
    
    Returns:
        Normalized JSON string
    """
    return format_json(json_text, indent=2, sort_keys=False, ensure_ascii=False)

def get_formatting_options() -> dict:
    """
    Get available formatting options and their descriptions.
    
    Returns:
        Dictionary of formatting options
    """
    return {
        "indent": {
            "description": "Number of spaces for indentation",
            "options": [0, 2, 4, 8],
            "default": 2
        },
        "sort_keys": {
            "description": "Sort object keys alphabetically",
            "options": [True, False],
            "default": False
        },
        "ensure_ascii": {
            "description": "Escape non-ASCII characters",
            "options": [True, False],
            "default": False
        },
        "separators": {
            "description": "Custom separators for items and key-value pairs",
            "compact": (",", ":"),
            "pretty": (", ", ": "),
            "default": (",", ": ")
        }
    }

def validate_and_format(
    json_text: str,
    indent: int = 2,
    sort_keys: bool = False,
    raise_on_error: bool = False
) -> tuple[bool, str, Optional[str]]:
    """
    Validate and format JSON in one operation.
    
    Args:
        json_text: JSON string to validate and format
        indent: Indentation level
        sort_keys: Whether to sort keys
        raise_on_error: Whether to raise exceptions on error
    
    Returns:
        Tuple of (success, formatted_json_or_original, error_message)
    """
    try:
        formatted = format_json(json_text, indent=indent, sort_keys=sort_keys)
        return True, formatted, None
    except json.JSONDecodeError as e:
        error_msg = f"JSON Syntax Error: {e.msg}"
        if hasattr(e, 'lineno') and hasattr(e, 'colno'):
            error_msg += f" (Line {e.lineno}, Column {e.colno})"
        if raise_on_error:
            raise
        return False, json_text, error_msg
    except Exception as e:
        error_msg = f"Formatting error: {str(e)}"
        if raise_on_error:
            raise
        return False, json_text, error_msg

def calculate_compression_ratio(original: str, formatted: str) -> dict:
    """
    Calculate compression statistics between original and formatted JSON.
    
    Args:
        original: Original JSON string
        formatted: Formatted JSON string
    
    Returns:
        Dictionary with compression statistics
    """
    original_size = len(original.encode('utf-8'))
    formatted_size = len(formatted.encode('utf-8'))
    
    if original_size == 0:
        return {"error": "Empty original JSON"}
    
    compression_ratio = formatted_size / original_size
    size_reduction = original_size - formatted_size
    percentage_change = ((formatted_size - original_size) / original_size) * 100
    
    return {
        "original_size": original_size,
        "formatted_size": formatted_size,
        "size_change": size_reduction,
        "compression_ratio": compression_ratio,
        "percentage_change": percentage_change,
        "is_smaller": formatted_size < original_size
    }