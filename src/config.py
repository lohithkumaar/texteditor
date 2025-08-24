"""
Configuration settings for the Text Tools app.
"""
from typing import Dict, Any

class Config:
    """Application configuration."""
    
    # File size limits
    MAX_FILE_SIZE_MB: int = 5
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
    
    # Text processing settings
    MAX_RECURSION_DEPTH: int = 8
    DEFAULT_INDENT: int = 2
    
    # Editor settings
    DEFAULT_EDITOR_HEIGHT: int = 400
    DEFAULT_EDITOR_LANGUAGE: str = "json"
    
    # Undo stack settings
    MAX_UNDO_STACK_SIZE: int = 3
    
    # Session state keys - Updated for general text editing
    SESSION_KEYS: Dict[str, Any] = {
        'original_text': '',
        'edited_text': '',
        'validator_text': '',
        'json_schema': '',
        'use_schema': False,
        'mode': 'Editor',
        'file_type': 'json',
        'undo_stack': []
    }
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS: list = ['.json', '.txt', '.md', '.markdown']
    
    # File type mappings
    FILE_TYPE_MAPPINGS: Dict[str, str] = {
        'json': 'json',
        'txt': 'text',
        'md': 'markdown',
        'markdown': 'markdown'
    }
    
    # Error messages
    ERROR_MESSAGES: Dict[str, str] = {
        'file_too_large': f'File size exceeds {MAX_FILE_SIZE_MB}MB limit',
        'invalid_json': 'Invalid JSON format',
        'schema_validation_failed': 'JSON does not match the provided schema',
        'file_read_error': 'Error reading file',
        'encoding_error': 'File encoding not supported',
        'empty_content': 'No content to process',
        'unsupported_file_type': 'Unsupported file type'
    }
