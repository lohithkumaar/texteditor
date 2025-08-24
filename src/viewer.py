"""
JSON tree viewer with expandable/collapsible structure for Text Tools.
"""

import streamlit as st
import json
from typing import Any, Dict, List, Union
from src.config import Config
from src.utils import get_json_type_icon, truncate_long_value, safe_json_key

def render_json_tree(
    data: Any,
    max_depth: int = Config.MAX_RECURSION_DEPTH,
    current_depth: int = 0,
    key_path: str = "root"
) -> None:
    """
    Render JSON data as an expandable tree structure.
    
    Args:
        data: JSON data to render
        max_depth: Maximum recursion depth
        current_depth: Current recursion level
        key_path: Current path in the JSON structure
    """
    if current_depth > max_depth:
        st.warning(f"⚠️ Maximum depth ({max_depth}) reached at {key_path}")
        return
    
    _render_json_node(data, current_depth, key_path, max_depth)

def _render_json_node(
    data: Any,
    depth: int,
    path: str,
    max_depth: int
) -> None:
    """Render a single JSON node."""
    if isinstance(data, dict):
        _render_dict_node(data, depth, path, max_depth)
    elif isinstance(data, list):
        _render_list_node(data, depth, path, max_depth)
    else:
        _render_value_node(data, path)

def _render_dict_node(
    data: Dict[str, Any],
    depth: int,
    path: str,
    max_depth: int
) -> None:
    """Render a dictionary node with expandable structure."""
    if not data:
        st.write("📁 {} (empty object)".format(path.split('.')[-1]))
        return
    
    # Create expandable section for the dictionary
    section_key = f"dict_{path}_{depth}"
    with st.expander(
        f"📁 {path.split('.')[-1]} ({len(data)} keys)",
        expanded=(depth < 2)
    ):
        # Sort keys if requested or show in original order
        keys = list(data.keys())
        for key in keys:
            safe_key = safe_json_key(key)
            child_path = f"{path}.{safe_key}" if path != "root" else safe_key
            
            # Create columns for key-value layout
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.write(f"**{safe_key}:**")
            
            with col2:
                if depth + 1 <= max_depth:
                    _render_json_node(data[key], depth + 1, child_path, max_depth)
                else:
                    st.write("...")

def _render_list_node(
    data: List[Any],
    depth: int,
    path: str,
    max_depth: int
) -> None:
    """Render a list node with expandable structure."""
    if not data:
        st.write("📋 {} (empty array)".format(path.split('.')[-1]))
        return
    
    # Create expandable section for the list
    with st.expander(
        f"📋 {path.split('.')[-1]} ({len(data)} items)",
        expanded=(depth < 2)
    ):
        for i, item in enumerate(data):
            child_path = f"{path}[{i}]"
            
            # Create columns for index-value layout
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.write(f"**[{i}]:**")
            
            with col2:
                if depth + 1 <= max_depth:
                    _render_json_node(item, depth + 1, child_path, max_depth)
                else:
                    st.write("...")
            
            # Limit number of items shown in very large arrays
            if i >= 99:  # Show max 100 items
                st.write(f"... and {len(data) - 100} more items")
                break

def _render_value_node(data: Any, path: str) -> None:
    """Render a primitive value node."""
    icon = get_json_type_icon(data)
    type_name = type(data).__name__
    
    if isinstance(data, str):
        # Handle long strings
        display_value = truncate_long_value(data, 100)
        if len(display_value) < len(data):
            # Show full string in expandable section
            with st.expander(f'{icon} "{display_value}" (string, {len(data)} chars)'):
                st.code(data, language="text")
        else:
            st.write(f'{icon} "{display_value}" ({type_name})')
    
    elif isinstance(data, bool):
        st.write(f"{icon} {str(data).lower()} ({type_name})")
    
    elif isinstance(data, (int, float)):
        st.write(f"{icon} {data} ({type_name})")
    
    elif data is None:
        st.write(f"{icon} null")
    
    else:
        # Handle other types
        display_value = truncate_long_value(str(data), 100)
        st.write(f"{icon} {display_value} ({type_name})")

def render_json_summary(data: Any) -> None:
    """
    Render a summary of the JSON structure.
    
    Args:
        data: Parsed JSON data
    """
    summary = analyze_json_structure(data)
    
    st.subheader("📊 JSON Summary")
    
    # Basic stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Keys", summary["total_keys"])
    
    with col2:
        st.metric("Max Depth", summary["max_depth"])
    
    with col3:
        st.metric("Array Items", summary["total_array_items"])
    
    with col4:
        st.metric("Null Values", summary["null_count"])
    
    # Type distribution
    if summary["type_distribution"]:
        st.subheader("🏷️ Type Distribution")
        for type_name, count in summary["type_distribution"].items():
            st.write(f"- **{type_name}**: {count}")

def analyze_json_structure(data: Any, current_depth: int = 0) -> Dict[str, Any]:
    """
    Analyze JSON structure and return statistics.
    
    Args:
        data: JSON data to analyze
        current_depth: Current recursion depth
    
    Returns:
        Dictionary with structure analysis
    """
    analysis = {
        "total_keys": 0,
        "max_depth": current_depth,
        "total_array_items": 0,
        "null_count": 0,
        "type_distribution": {}
    }
    
    def _count_type(value: Any):
        """Count value types."""
        type_name = type(value).__name__
        if value is None:
            type_name = "null"
        analysis["type_distribution"][type_name] = (
            analysis["type_distribution"].get(type_name, 0) + 1
        )
        
        if value is None:
            analysis["null_count"] += 1
    
    def _analyze_recursive(obj: Any, depth: int):
        """Recursively analyze structure."""
        analysis["max_depth"] = max(analysis["max_depth"], depth)
        
        if isinstance(obj, dict):
            analysis["total_keys"] += len(obj)
            _count_type(obj)
            for value in obj.values():
                _analyze_recursive(value, depth + 1)
        elif isinstance(obj, list):
            analysis["total_array_items"] += len(obj)
            _count_type(obj)
            for item in obj:
                _analyze_recursive(item, depth + 1)
        else:
            _count_type(obj)
    
    _analyze_recursive(data, current_depth)
    return analysis

def render_json_path_explorer(data: Any) -> None:
    """
    Render a path explorer for navigating JSON structure.
    
    Args:
        data: Parsed JSON data
    """
    st.subheader("🗺️ Path Explorer")
    
    paths = extract_all_paths(data)
    if not paths:
        st.info("No paths found in JSON structure.")
        return
    
    # Path selector
    selected_path = st.selectbox(
        "Select a path to explore:",
        paths,
        help="Choose a JSON path to see its value"
    )
    
    if selected_path:
        try:
            value = get_value_at_path(data, selected_path)
            st.write(f"**Path:** `{selected_path}`")
            st.write("**Value:**")
            if isinstance(value, (dict, list)):
                st.json(value)
            else:
                st.code(str(value))
        except Exception as e:
            st.error(f"Error accessing path: {str(e)}")

def extract_all_paths(data: Any, current_path: str = "") -> List[str]:
    """
    Extract all possible paths from JSON data.
    
    Args:
        data: JSON data
        current_path: Current path string
    
    Returns:
        List of all paths in the JSON
    """
    paths = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{current_path}.{key}" if current_path else key
            paths.append(new_path)
            if isinstance(value, (dict, list)):
                paths.extend(extract_all_paths(value, new_path))
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_path = f"{current_path}[{i}]"
            paths.append(new_path)
            if isinstance(item, (dict, list)):
                paths.extend(extract_all_paths(item, new_path))
    
    return paths

def get_value_at_path(data: Any, path: str) -> Any:
    """
    Get value at a specific JSON path.
    
    Args:
        data: JSON data
        path: Path string (e.g., "user.profile.name" or "items[0].id")
    
    Returns:
        Value at the specified path
    
    Raises:
        KeyError: If path doesn't exist
        IndexError: If array index is out of range
    """
    if not path:
        return data
    
    current = data
    
    # Split path into components
    parts = []
    current_part = ""
    i = 0
    
    while i < len(path):
        if path[i] == '.':
            if current_part:
                parts.append(current_part)
                current_part = ""
        elif path[i] == '[':
            if current_part:
                parts.append(current_part)
                current_part = ""
            # Find the closing bracket
            j = i + 1
            while j < len(path) and path[j] != ']':
                j += 1
            if j < len(path):
                parts.append(int(path[i+1:j]))
                i = j
            else:
                raise ValueError(f"Unclosed bracket in path: {path}")
        else:
            current_part += path[i]
        i += 1
    
    if current_part:
        parts.append(current_part)
    
    # Navigate through the path
    for part in parts:
        if isinstance(part, int):
            current = current[part]
        else:
            current = current[part]
    
    return current