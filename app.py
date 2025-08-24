"""
Text Tools · JSON Validator · Formatter · Editor · Viewer

Main Streamlit application entry point.
"""

import streamlit as st
import json
from typing import Dict, Any, Optional
import difflib
from src.config import Config
from src.editor import render_editor
from src.validator import validate_json, validate_against_schema
from src.formatter import format_json, minify_json
from src.viewer import render_json_tree
from src.utils import sanitize_text, init_session_state, add_to_undo_stack, detect_file_type

def main():
    """Main application function."""
    st.set_page_config(
        page_title="Text Tools · JSON Validator · Formatter · Editor · Viewer",
        page_icon="🛠️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    st.title("🛠️ Text Tools · JSON Validator · Formatter · Editor · Viewer")
    st.markdown("Upload, validate, format, edit, and view text files (JSON, TXT, MD) with ease.")
    
    # Sidebar
    render_sidebar()
    
    # Main content area
    render_main_content()

def render_sidebar():
    """Render the sidebar with controls."""
    st.sidebar.header("Controls")
    
    # Mode selector
    mode = st.sidebar.selectbox(
        "Mode",
        ["Editor", "Viewer", "Validator", "Diff"],
        key="mode"
    )
    
    st.sidebar.markdown("---")
    
    # Upload/Paste area
    st.sidebar.subheader("Input Text/JSON")
    
    # File upload - support multiple file types
    uploaded_file = st.sidebar.file_uploader(
        "Upload file",
        type=['json', 'txt', 'md'],
        help="Upload a JSON, TXT, or MD file to edit, validate, or format"
    )
    
    # Text input
    text_input = st.sidebar.text_area(
        "Or paste text here:",
        height=150,
        placeholder='{\n  "example": "value"\n}\n\nor any text content...',
        help="Paste JSON or any text content directly"
    )
    
    # Process input - avoid unnecessary reruns
    if uploaded_file is not None:
        try:
            content = uploaded_file.read().decode('utf-8')
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            # Only update if content actually changed
            if content != st.session_state.get('original_text', ''):
                st.session_state.original_text = content
                st.session_state.edited_text = content
                st.session_state.file_type = file_extension if file_extension in ['json', 'txt', 'md'] else detect_file_type(content, uploaded_file.name)
                # Don't call st.rerun() here to avoid refresh
        except Exception as e:
            st.sidebar.error(f"Error reading file: {str(e)}")
    elif text_input and text_input != st.session_state.get('original_text', ''):
        st.session_state.original_text = text_input
        st.session_state.edited_text = text_input
        st.session_state.file_type = detect_file_type(text_input)
        # Don't call st.rerun() here to avoid refresh
    
    st.sidebar.markdown("---")
    
    # Schema validation toggle (only show for JSON mode)
    current_mode = st.session_state.get('mode', 'Editor')
    if current_mode in ["Validator", "Viewer"] or st.session_state.get('file_type', 'json') == 'json':
        use_schema = st.sidebar.checkbox("Validate against JSON Schema", key="use_schema")
        if use_schema:
            schema_file = st.sidebar.file_uploader(
                "Upload JSON Schema",
                type=['json'],
                key="schema_upload"
            )
            
            if schema_file:
                try:
                    schema_content = schema_file.read().decode('utf-8')
                    st.session_state.json_schema = schema_content
                except Exception as e:
                    st.sidebar.error(f"Error reading schema: {str(e)}")
    
    st.sidebar.markdown("---")
    
    # Format settings (only show for JSON)
    if st.session_state.get('file_type', 'json') == 'json':
        st.sidebar.subheader("JSON Format Settings")
        indent = st.sidebar.selectbox(
            "Indentation",
            [2, 4, 0],
            index=0,
            help="0 = minified (no spaces)"
        )
        sort_keys = st.sidebar.checkbox("Sort keys", value=False)
    else:
        indent = 2
        sort_keys = False
    
    st.sidebar.markdown("---")
    
    # Action buttons
    st.sidebar.subheader("Actions")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.session_state.get('file_type', 'json') == 'json':
            if st.button("Validate JSON", use_container_width=True):
                validate_current_json()
            if st.button("Format JSON", use_container_width=True):
                format_current_json(indent, sort_keys)
        else:
            if st.button("Word Count", use_container_width=True):
                show_text_stats()
        
        if st.button("Reset", use_container_width=True):
            reset_text()
    
    with col2:
        if st.session_state.get('file_type', 'json') == 'json':
            if st.button("Minify JSON", use_container_width=True):
                minify_current_json()
        else:
            if st.button("Clear", use_container_width=True):
                clear_text()
        
        if st.button("Download", use_container_width=True):
            # Set session state to show download options
            st.session_state.show_download = True
        if st.button("Undo", use_container_width=True):
            undo_changes()

def render_main_content():
    """Render the main content area based on selected mode."""
    mode = st.session_state.get('mode', 'Editor')
    
    # Show download options if requested
    if st.session_state.get('show_download', False):
        render_download_interface()
        st.markdown("---")
    
    if mode == "Editor":
        render_editor_mode()
    elif mode == "Viewer":
        render_viewer_mode()
    elif mode == "Validator":
        render_validator_mode()
    elif mode == "Diff":
        render_diff_mode()

def render_download_interface():
    """Render persistent download interface."""
    current_text = st.session_state.get('edited_text', '')
    if not current_text:
        st.warning("No content to download.")
        if st.button("Close Download", key="close_download_empty"):
            st.session_state.show_download = False
            st.rerun()
        return
    
    st.subheader("📥 Download Options")
    
    # Create columns for layout
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # File type selection
        download_type = st.selectbox(
            "Choose download format:",
            ["json", "txt", "md"],
            index=0 if st.session_state.get('file_type', 'json') == 'json' else 
                  (1 if st.session_state.get('file_type', 'json') == 'txt' else 2),
            help="Select the file format for download",
            key="download_type_select"
        )
    
    with col2:
        # File name
        filename = st.text_input(
            "Filename (without extension):",
            value="edited",
            help="Enter the filename without extension",
            key="download_filename"
        )
    
    with col3:
        # Close button
        if st.button("✕ Close", key="close_download", help="Close download options"):
            st.session_state.show_download = False
            st.rerun()
    
    # MIME type mapping
    mime_type_map = {
        'json': 'application/json',
        'txt': 'text/plain',
        'md': 'text/markdown'
    }
    
    # Download button row
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # Download button
        st.download_button(
            label=f"📥 Download as {download_type.upper()}",
            data=current_text,
            file_name=f"{filename}.{download_type}",
            mime=mime_type_map.get(download_type, 'text/plain'),
            help=f"Download the current content as {download_type.upper()} file",
            key="main_download_button"
        )
    
    with col2:
        # Copy to clipboard info
        st.info("💡 Use Ctrl+A, Ctrl+C to copy all content")

def render_editor_mode():
    """Render the general editor interface."""
    file_type = st.session_state.get('file_type', 'json')
    
    # Show proper title based on detected file type
    file_type_display = {
        'json': 'JSON',
        'txt': 'Text',
        'md': 'Markdown'
    }
    display_type = file_type_display.get(file_type, file_type.upper())
    st.subheader(f"Text Editor ({display_type})")
    
    current_text = st.session_state.get('edited_text', '')
    
    # Determine language for syntax highlighting
    language_map = {
        'json': 'json',
        'md': 'markdown',
        'txt': 'text'
    }
    language = language_map.get(file_type, 'text')
    
    # Use a STABLE key that doesn't change with content
    editor_key = f"main_editor_{file_type}"
    
    # Render editor - REMOVED the content change detection that caused refresh
    edited_content = render_editor(
        current_text,
        key=editor_key,
        height=400,
        language=language
    )
    
    # Only update session state if content actually changed and is different
    if edited_content and edited_content != current_text:
        # Don't add to undo stack on every keystroke - only on significant changes
        if len(edited_content) - len(current_text) > 10 or len(current_text) - len(edited_content) > 10:
            add_to_undo_stack(current_text)
        st.session_state.edited_text = edited_content
    
    # Show file info
    if current_text:
        show_file_info(current_text, file_type)

def render_viewer_mode():
    """Render the viewer interface."""
    st.subheader("Content Viewer")
    
    current_text = st.session_state.get('edited_text', '')
    file_type = st.session_state.get('file_type', 'json')
    
    if not current_text:
        st.info("Upload or paste content to view it here.")
        return
    
    if file_type == 'json':
        # Parse and display JSON
        try:
            parsed_json = json.loads(current_text)
            
            # Show tree view
            st.markdown("### Tree View")
            render_json_tree(parsed_json)
            
            # Show formatted text
            st.markdown("### Formatted Text")
            formatted = format_json(current_text, indent=2, sort_keys=False)
            st.code(formatted, language="json")
            
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e.msg} at line {e.lineno}, column {e.colno}")
    else:
        # Display text content
        st.markdown("### Content")
        if file_type == 'md':
            # Render markdown
            st.markdown(current_text)
            st.markdown("### Raw Markdown")
            st.code(current_text, language="markdown")
        else:
            # Display as text
            st.code(current_text, language="text")

def render_validator_mode():
    """Render the validator interface with editor."""
    st.subheader("JSON Validator with Editor")
    
    # Add editor for validation
    st.markdown("### Edit JSON to Validate")
    
    # Get current content or start with empty
    validator_content = st.session_state.get('validator_text', st.session_state.get('edited_text', ''))
    
    # Use STABLE key for validator editor
    validator_key = "validator_editor_stable"
    edited_validator_content = render_editor(
        validator_content,
        key=validator_key,
        height=300,
        language="json"
    )
    
    # Update session state if content changed
    if edited_validator_content and edited_validator_content != validator_content:
        st.session_state.validator_text = edited_validator_content
    
    st.markdown("---")
    
    # Validate button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        validate_btn = st.button("🔍 Validate JSON", type="primary")
    
    with col2:
        if st.button("📋 Copy from Editor"):
            st.session_state.validator_text = st.session_state.get('edited_text', '')
            st.rerun()
    
    # Show validation results when button is clicked
    if validate_btn:
        current_json = st.session_state.get('validator_text', '')
        if not current_json:
            st.warning("No JSON to validate.")
        else:
            st.markdown("### Validation Results")
            
            # Validate JSON syntax
            is_valid, errors = validate_json(current_json)
            
            if is_valid:
                st.success("✅ Valid JSON syntax")
                
                # Schema validation if enabled
                if st.session_state.get('use_schema', False) and st.session_state.get('json_schema'):
                    schema_errors = validate_against_schema(current_json, st.session_state.json_schema)
                    if not schema_errors:
                        st.success("✅ Valid against JSON Schema")
                    else:
                        st.error("❌ Schema validation errors:")
                        for error in schema_errors:
                            st.error(f"Path: {error['path']} - {error['message']}")
            else:
                st.error("❌ Invalid JSON syntax")
                for error in errors:
                    # Display detailed error information
                    st.code(error, language="text")

def render_diff_mode():
    """Render the diff interface with manual input capability."""
    st.subheader("Text Diff")
    
    # Create two columns for manual input
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Original**")
        original_manual = st.text_area(
            "Original Text",
            value=st.session_state.get('original_text', ''),
            height=300,
            key="diff_original"
        )
    
    with col2:
        st.markdown("**Modified**")
        modified_manual = st.text_area(
            "Modified Text", 
            value=st.session_state.get('edited_text', ''),
            height=300,
            key="diff_modified"
        )
    
    # Update session state with manual inputs
    if original_manual != st.session_state.get('original_text', ''):
        st.session_state.original_text = original_manual
    
    if modified_manual != st.session_state.get('edited_text', ''):
        st.session_state.edited_text = modified_manual
    
    original = st.session_state.get('original_text', '')
    edited = st.session_state.get('edited_text', '')
    
    if not original and not edited:
        st.info("Enter text content in both text areas above to compare.")
        return
    
    if original == edited:
        st.success("No changes detected.")
        return
    
    # Show diff
    st.markdown("---")
    diff_type = st.radio("Diff view:", ["Side by side", "Unified"], horizontal=True)
    
    if diff_type == "Side by side":
        show_side_by_side_diff(original, edited)
    else:
        show_unified_diff(original, edited)

def show_side_by_side_diff(original: str, edited: str):
    """Show side-by-side diff with highlighting."""
    original_lines = original.splitlines()
    edited_lines = edited.splitlines()
    
    # Get line-by-line diff
    differ = difflib.unified_diff(original_lines, edited_lines, lineterm='')
    diff_lines = list(differ)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Original**")
        original_html = []
        for i, line in enumerate(original_lines, 1):
            # Check if this line is deleted
            is_deleted = any(f"-{line}" in d for d in diff_lines)
            if is_deleted:
                original_html.append(f'<div style="background-color: #ffebee; color: #c62828; padding: 2px;">{i:3d}: {line}</div>')
            else:
                original_html.append(f'<div style="padding: 2px;">{i:3d}: {line}</div>')
        
        st.markdown('<div style="font-family: monospace; font-size: 12px;">' + '\n'.join(original_html) + '</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("**Modified**")
        edited_html = []
        for i, line in enumerate(edited_lines, 1):
            # Check if this line is added
            is_added = any(f"+{line}" in d for d in diff_lines)
            if is_added:
                edited_html.append(f'<div style="background-color: #e8f5e8; color: #2e7d32; padding: 2px;">{i:3d}: {line}</div>')
            else:
                edited_html.append(f'<div style="padding: 2px;">{i:3d}: {line}</div>')
        
        st.markdown('<div style="font-family: monospace; font-size: 12px;">' + '\n'.join(edited_html) + '</div>', unsafe_allow_html=True)

def show_unified_diff(original: str, edited: str):
    """Show unified diff."""
    original_lines = original.splitlines(keepends=True)
    edited_lines = edited.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines,
        edited_lines,
        fromfile="original",
        tofile="modified",
        lineterm=""
    )
    
    diff_text = ''.join(diff)
    if diff_text:
        st.code(diff_text, language="diff")
    else:
        st.info("No differences found.")

def show_file_info(content: str, file_type: str):
    """Show file statistics."""
    st.markdown("---")
    st.markdown("### File Information")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Characters", len(content))
    
    with col2:
        word_count = len(content.split()) if content else 0
        st.metric("Words", word_count)
    
    with col3:
        line_count = len(content.splitlines()) if content else 0
        st.metric("Lines", line_count)
    
    with col4:
        size_bytes = len(content.encode('utf-8'))
        size_kb = size_bytes / 1024
        st.metric("Size", f"{size_kb:.1f} KB")

def show_download_options():
    """Show download options with file type selection."""
    # This function is now replaced by render_download_interface()
    # Keeping it for backward compatibility, but it just sets the session state
    st.session_state.show_download = True

def validate_current_json():
    """Validate the current JSON and show results."""
    current_json = st.session_state.get('edited_text', '')
    if not current_json:
        st.warning("No JSON to validate.")
        return
    
    is_valid, errors = validate_json(current_json)
    if is_valid:
        st.success("✅ JSON is valid!")
    else:
        st.error("❌ JSON validation failed:")
        for error in errors:
            st.code(error, language="text")

def format_current_json(indent: int, sort_keys: bool):
    """Format the current JSON."""
    current_json = st.session_state.get('edited_text', '')
    if not current_json:
        st.warning("No JSON to format.")
        return
    
    try:
        if indent == 0:
            formatted = minify_json(current_json)
            success_msg = "JSON minified successfully!"
        else:
            formatted = format_json(current_json, indent=indent, sort_keys=sort_keys)
            success_msg = "JSON formatted successfully!"
        
        add_to_undo_stack(current_json)
        st.session_state.edited_text = formatted
        st.success(success_msg)
        
    except Exception as e:
        st.error(f"Error formatting JSON: {str(e)}")

def minify_current_json():
    """Minify the current JSON."""
    current_json = st.session_state.get('edited_text', '')
    if not current_json:
        st.warning("No JSON to minify.")
        return
    
    try:
        minified = minify_json(current_json)
        add_to_undo_stack(current_json)
        st.session_state.edited_text = minified
        st.success("JSON minified successfully!")
        
    except Exception as e:
        st.error(f"Error minifying JSON: {str(e)}")

def show_text_stats():
    """Show text statistics."""
    current_text = st.session_state.get('edited_text', '')
    if not current_text:
        st.warning("No text to analyze.")
        return
    
    # Calculate stats
    char_count = len(current_text)
    word_count = len(current_text.split())
    line_count = len(current_text.splitlines())
    paragraph_count = len([p for p in current_text.split('\n\n') if p.strip()])
    
    st.info(f"📊 **Text Stats:** {char_count} characters, {word_count} words, {line_count} lines, {paragraph_count} paragraphs")

def clear_text():
    """Clear the current text."""
    if st.session_state.get('edited_text'):
        add_to_undo_stack(st.session_state.get('edited_text', ''))
        st.session_state.edited_text = ''
        st.success("Text cleared!")
    else:
        st.warning("No text to clear.")

def reset_text():
    """Reset text to original state."""
    if st.session_state.get('original_text'):
        add_to_undo_stack(st.session_state.get('edited_text', ''))
        st.session_state.edited_text = st.session_state.original_text
        st.success("Text reset to original!")
    else:
        st.warning("No original text to reset to.")

def undo_changes():
    """Undo the last change."""
    undo_stack = st.session_state.get('undo_stack', [])
    if undo_stack:
        previous_state = undo_stack.pop()
        st.session_state.edited_text = previous_state
        st.session_state.undo_stack = undo_stack
        st.success("Changes undone!")
    else:
        st.warning("No changes to undo.")

if __name__ == "__main__":
    main()