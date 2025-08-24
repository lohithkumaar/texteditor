"""
Unit tests for utility functions and core JSON processing for Text Tools.
"""

import pytest
import json
from src.formatter import format_json, minify_json, validate_and_format
from src.validator import validate_json, validate_against_schema
from src.utils import sanitize_text, safe_json_key, truncate_long_value, get_json_type_icon

class TestFormatter:
    """Test JSON formatting functions."""
    
    def test_format_json_valid(self):
        """Test formatting valid JSON."""
        input_json = '{"name":"test","value":123}'
        expected = '{\n  "name": "test",\n  "value": 123\n}'
        result = format_json(input_json, indent=2, sort_keys=False)
        assert result == expected
    
    def test_format_json_with_sorting(self):
        """Test formatting with key sorting."""
        input_json = '{"z":1,"a":2,"m":3}'
        result = format_json(input_json, indent=2, sort_keys=True)
        
        # Parse to verify structure and order
        parsed = json.loads(result)
        keys = list(parsed.keys())
        assert keys == ["a", "m", "z"]
    
    def test_format_json_invalid(self):
        """Test formatting invalid JSON raises error."""
        invalid_json = '{"name":"test"'  # Missing closing brace
        with pytest.raises(json.JSONDecodeError):
            format_json(invalid_json)
    
    def test_minify_json(self):
        """Test JSON minification."""
        input_json = '{\n  "name": "test",\n  "value": 123\n}'
        expected = '{"name":"test","value":123}'
        result = minify_json(input_json)
        assert result == expected
    
    def test_validate_and_format_valid(self):
        """Test combined validation and formatting."""
        input_json = '{"test":true}'
        success, formatted, error = validate_and_format(input_json, indent=2)
        
        assert success is True
        assert error is None
        assert '"test": true' in formatted
    
    def test_validate_and_format_invalid(self):
        """Test combined validation and formatting with invalid JSON."""
        invalid_json = '{"test":}'
        success, result, error = validate_and_format(invalid_json, raise_on_error=False)
        
        assert success is False
        assert result == invalid_json  # Returns original on error
        assert error is not None
        assert "Syntax Error" in error

class TestValidator:
    """Test JSON validation functions."""
    
    def test_validate_json_valid(self):
        """Test validation of valid JSON."""
        valid_json = '{"name":"test","items":[1,2,3]}'
        is_valid, errors = validate_json(valid_json)
        
        assert is_valid is True
        assert errors == []
    
    def test_validate_json_invalid(self):
        """Test validation of invalid JSON."""
        invalid_json = '{"name":"test"'  # Missing closing brace
        is_valid, errors = validate_json(invalid_json)
        
        assert is_valid is False
        assert len(errors) > 0
        assert "Parse error on line" in errors[0]
    
    def test_validate_json_empty(self):
        """Test validation of empty JSON."""
        is_valid, errors = validate_json("")
        
        assert is_valid is False
        assert "Empty JSON input" in errors[0]
    
    def test_validate_against_schema_valid(self):
        """Test schema validation with valid data."""
        json_data = '{"name":"John","age":30}'
        schema = '''{
            "type": "object",
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0}
            }
        }'''
        
        errors = validate_against_schema(json_data, schema)
        assert errors == []
    
    def test_validate_against_schema_invalid(self):
        """Test schema validation with invalid data."""
        json_data = '{"name":"John","age":"thirty"}'  # age should be integer
        schema = '''{
            "type": "object",
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        }'''
        
        errors = validate_against_schema(json_data, schema)
        assert len(errors) > 0
        assert any("age" in error["path"] for error in errors)

class TestUtils:
    """Test utility functions."""
    
    def test_sanitize_text(self):
        """Test text sanitization."""
        dirty_text = "<script>alert('xss')</script>Hello"
        clean_text = sanitize_text(dirty_text)
        assert "<script>" not in clean_text
        assert "Hello" in clean_text
    
    def test_sanitize_text_long(self):
        """Test text sanitization with length limit."""
        long_text = "a" * 2000
        sanitized = sanitize_text(long_text, max_length=100)
        assert len(sanitized) == 100
    
    def test_safe_json_key(self):
        """Test JSON key sanitization."""
        key = "<script>badkey</script>"
        safe_key = safe_json_key(key)
        assert "<script>" not in safe_key
    
    def test_safe_json_key_non_string(self):
        """Test JSON key sanitization with non-string input."""
        key = 123
        safe_key = safe_json_key(key)
        assert safe_key == "123"
    
    def test_truncate_long_value(self):
        """Test value truncation."""
        long_value = "This is a very long string that should be truncated"
        truncated = truncate_long_value(long_value, max_length=20)
        assert len(truncated) <= 23  # 20 + "..." = 23
        assert "..." in truncated
    
    def test_truncate_short_value(self):
        """Test that short values are not truncated."""
        short_value = "Short"
        result = truncate_long_value(short_value, max_length=20)
        assert result == short_value
        assert "..." not in result
    
    def test_get_json_type_icon(self):
        """Test JSON type icon assignment."""
        assert get_json_type_icon({}) == "📁"  # dict
        assert get_json_type_icon([]) == "📋"  # list
        assert get_json_type_icon("string") == "📝"  # string
        assert get_json_type_icon(123) == "🔢"  # number
        assert get_json_type_icon(True) == "☑️"  # boolean true
        assert get_json_type_icon(False) == "☐"  # boolean false
        assert get_json_type_icon(None) == "∅"  # null

class TestValidatorEnhancements:
    """Test enhanced validator functionality."""
    
    def test_detailed_error_message(self):
        """Test that detailed error messages include line information."""
        invalid_json = '''{
            "name": "test",
            "invalid": 
        }'''
        
        is_valid, errors = validate_json(invalid_json)
        assert is_valid is False
        assert len(errors) > 0
        
        error_msg = errors[0]
        assert "Parse error on line" in error_msg
        assert "^" in error_msg  # Should have pointer indicator
    
    def test_complex_error_detection(self):
        """Test error detection in complex JSON structures."""
        invalid_json = '''{
            "user": {
                "name": "John",
                "email": "john@example.com"
                "age": 30
            }
        }'''
        
        is_valid, errors = validate_json(invalid_json)
        assert is_valid is False
        assert "Parse error on line" in errors[0]
    
    def test_trailing_comma_error(self):
        """Test detection of trailing comma errors."""
        invalid_json = '''{
            "name": "test",
            "value": 123,
        }'''
        
        is_valid, errors = validate_json(invalid_json)
        assert is_valid is False
        # Error message should be descriptive
        error_msg = errors[0].lower()
        assert any(word in error_msg for word in ["comma", "expecting", "parse"])

if __name__ == "__main__":
    pytest.main([__file__])
