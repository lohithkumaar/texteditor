"""
JSON validation functions for syntax and schema validation.
Enhanced with detailed error reporting including line numbers and context.
"""

import json
import jsonschema
from typing import List, Dict, Tuple, Any, Optional
import re

# Try to import ijson for streaming large files
try:
    import ijson
    IJSON_AVAILABLE = True
except ImportError:
    IJSON_AVAILABLE = False

def validate_json(json_text: str) -> Tuple[bool, List[str]]:
    """
    Validate JSON syntax and return detailed error information.
    
    Args:
        json_text: JSON string to validate
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    if not json_text.strip():
        return False, ["Empty JSON input"]
    
    try:
        json.loads(json_text)
        return True, []
    except json.JSONDecodeError as e:
        # Create detailed error message with context
        detailed_error = _create_detailed_error_message(json_text, e)
        return False, [detailed_error]
    except Exception as e:
        return False, [f"Unexpected error: {str(e)}"]

def _create_detailed_error_message(json_text: str, error: json.JSONDecodeError) -> str:
    """
    Create a detailed error message with line context and visual indicators.
    
    Args:
        json_text: Original JSON text
        error: JSONDecodeError object
    
    Returns:
        Formatted error message with context
    """
    lines = json_text.splitlines()
    line_num = getattr(error, 'lineno', 1)
    col_num = getattr(error, 'colno', 1)
    
    # Build the error message
    error_msg = f"Error: Parse error on line {line_num}:\n"
    
    # Add context lines (show 1 line before and after if possible)
    context_lines = []
    start_line = max(0, line_num - 2)
    end_line = min(len(lines), line_num + 1)
    
    for i in range(start_line, end_line):
        line_content = lines[i] if i < len(lines) else ""
        line_number = i + 1
        
        if line_number == line_num:
            # This is the error line - add visual indicator
            context_lines.append(f"{line_content}")
            
            # Add pointer to exact error position
            pointer_line = "-" * (col_num - 1) + "^"
            context_lines.append(pointer_line)
        else:
            context_lines.append(f"{line_content}")
    
    # Join context lines
    context = "\n".join(context_lines)
    
    # Add the context to error message
    if context.strip():
        # Truncate very long lines for readability
        context_lines_truncated = []
        for line in context.split('\n'):
            if len(line) > 100:
                line = line[:97] + "..."
            context_lines_truncated.append(line)
        context = "\n".join(context_lines_truncated)
        error_msg += f"...{context}\n"
    
    # Add specific error description
    error_description = _get_error_description(error)
    error_msg += f"{error_description}"
    
    return error_msg

def _get_error_description(error: json.JSONDecodeError) -> str:
    """
    Get a user-friendly description of the JSON error.
    
    Args:
        error: JSONDecodeError object
        
    Returns:
        Descriptive error message
    """
    msg = error.msg.lower()
    
    if "expecting" in msg:
        return f"Expecting {error.msg.split('Expecting')[1].strip()}"
    elif "unterminated string" in msg:
        return "Unterminated string literal - missing closing quote"
    elif "invalid control character" in msg:
        return "Invalid control character in string"
    elif "invalid escape sequence" in msg:
        return "Invalid escape sequence in string"
    elif "duplicate keys" in msg:
        return "Duplicate keys found in JSON object"
    elif "trailing comma" in msg:
        return "Trailing comma not allowed in JSON"
    else:
        # Try to provide more context based on common patterns
        if "}" in msg:
            return "Missing closing brace '}' or invalid object structure"
        elif "]" in msg:
            return "Missing closing bracket ']' or invalid array structure"
        elif "," in msg:
            return "Missing comma ',' between elements or trailing comma"
        elif ":" in msg:
            return "Missing colon ':' after object key or invalid key-value syntax"
        else:
            return f"JSON syntax error: {error.msg}"

def validate_against_schema(json_text: str, schema_text: str) -> List[Dict[str, str]]:
    """
    Validate JSON against a JSON Schema.
    
    Args:
        json_text: JSON string to validate
        schema_text: JSON Schema string
    
    Returns:
        List of validation errors with path and message
    """
    errors = []
    
    try:
        # Parse JSON data
        json_data = json.loads(json_text)
    except json.JSONDecodeError as e:
        return [{"path": "root", "message": f"Invalid JSON: {e.msg}"}]
    
    try:
        # Parse schema
        schema = json.loads(schema_text)
    except json.JSONDecodeError as e:
        return [{"path": "schema", "message": f"Invalid schema: {e.msg}"}]
    
    try:
        # Validate against schema
        jsonschema.validate(json_data, schema)
        return []  # No errors
    except jsonschema.ValidationError as e:
        # Convert validation error to our format
        error_path = _format_json_path(e.absolute_path)
        errors.append({
            "path": error_path,
            "message": e.message
        })
        return errors
    except jsonschema.SchemaError as e:
        return [{"path": "schema", "message": f"Invalid schema: {e.message}"}]
    except Exception as e:
        return [{"path": "unknown", "message": f"Validation error: {str(e)}"}]

def validate_large_json(json_text: str, max_size_mb: int = 5) -> Tuple[bool, List[str]]:
    """
    Validate large JSON files using streaming parser if available.
    
    Args:
        json_text: JSON string to validate
        max_size_mb: Maximum size in MB before using streaming
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    # Check size
    size_bytes = len(json_text.encode('utf-8'))
    size_mb = size_bytes / (1024 * 1024)
    
    if size_mb <= max_size_mb or not IJSON_AVAILABLE:
        # Use regular validation for smaller files or if ijson not available
        return validate_json(json_text)
    
    # Use streaming validation for large files
    try:
        import io
        json_stream = io.StringIO(json_text)
        
        # Try to parse using ijson streaming parser
        try:
            parser = ijson.parse(json_stream)
            for _ in parser:
                pass  # Just iterate through to check for errors
            return True, []
        except ijson.JSONError as e:
            return False, [f"Large JSON parsing error: {str(e)}"]
        except Exception as e:
            return False, [f"Streaming validation failed: {str(e)}"]
    
    except Exception:
        # Fall back to regular validation if streaming fails
        return validate_json(json_text)

def _get_error_context(json_text: str, error_pos: int, context_length: int = 50) -> str:
    """
    Get context around the error position.
    
    Args:
        json_text: Full JSON text
        error_pos: Position of error
        context_length: Length of context to show on each side
    
    Returns:
        Context string around the error
    """
    if error_pos < 0 or error_pos >= len(json_text):
        return ""
    
    start = max(0, error_pos - context_length)
    end = min(len(json_text), error_pos + context_length)
    context = json_text[start:end]
    
    # Mark the error position
    marker_pos = error_pos - start
    if 0 <= marker_pos < len(context):
        context = context[:marker_pos] + "❌" + context[marker_pos:]
    
    return context

def _format_json_path(path) -> str:
    """
    Format JSONSchema validation path for display.
    
    Args:
        path: JSONSchema path object
    
    Returns:
        Formatted path string
    """
    if not path:
        return "root"
    
    path_parts = []
    for part in path:
        if isinstance(part, int):
            path_parts.append(f"[{part}]")
        else:
            if path_parts:  # Not the first element
                path_parts.append(f".{part}")
            else:
                path_parts.append(str(part))
    
    return "".join(path_parts) or "root"

def get_validation_summary(json_text: str, schema_text: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a comprehensive validation summary.
    
    Args:
        json_text: JSON text to validate
        schema_text: Optional schema for validation
    
    Returns:
        Dictionary with validation results
    """
    summary = {
        "syntax_valid": False,
        "syntax_errors": [],
        "schema_valid": None,
        "schema_errors": [],
        "size_info": {},
        "recommendations": []
    }
    
    # Syntax validation
    is_valid, errors = validate_json(json_text)
    summary["syntax_valid"] = is_valid
    summary["syntax_errors"] = errors
    
    # Size information
    size_bytes = len(json_text.encode('utf-8'))
    summary["size_info"] = {
        "bytes": size_bytes,
        "kb": size_bytes / 1024,
        "mb": size_bytes / (1024 * 1024),
        "is_large": size_bytes > 5 * 1024 * 1024
    }
    
    # Schema validation if provided
    if schema_text and is_valid:
        schema_errors = validate_against_schema(json_text, schema_text)
        summary["schema_valid"] = len(schema_errors) == 0
        summary["schema_errors"] = schema_errors
    
    # Generate recommendations
    if summary["size_info"]["is_large"]:
        summary["recommendations"].append(
            "Consider breaking large JSON into smaller files for better performance"
        )
    
    if not is_valid:
        summary["recommendations"].append(
            "Fix syntax errors before proceeding with formatting or schema validation"
        )
    
    return summary