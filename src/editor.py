"""
Text editor component with syntax highlighting for Text Tools.

Falls back to text_area if streamlit-ace is not available.
"""

import streamlit as st
from typing import Optional

# Try to import streamlit-ace, fall back to text_area if not available
try:
    from streamlit_ace import st_ace
    ACE_AVAILABLE = True
except ImportError:
    ACE_AVAILABLE = False

def render_editor(
    text: str,
    key: str,
    height: int = 400,
    language: str = "json",
    theme: str = "monokai",
    wrap: bool = False,
    auto_update: bool = False  # Changed default to False to prevent refresh
) -> str:
    """
    Render a text editor with syntax highlighting.
    
    Args:
        text: Initial text content
        key: Unique key for the editor component
        height: Editor height in pixels
        language: Programming language for syntax highlighting
        theme: Editor theme (only used with ACE)
        wrap: Whether to wrap long lines
        auto_update: Whether to auto-update on change (set to False to prevent refresh)
    
    Returns:
        Current editor content
    """
    if ACE_AVAILABLE:
        return _render_ace_editor(text, key, height, language, theme, wrap, auto_update)
    else:
        return _render_text_area_fallback(text, key, height)

def _render_ace_editor(
    text: str,
    key: str,
    height: int,
    language: str,
    theme: str,
    wrap: bool,
    auto_update: bool
) -> str:
    """Render ACE editor with advanced features."""
    # Available themes for ACE
    themes = [
        "monokai", "github", "tomorrow", "kuroir", "twilight", "xcode",
        "textmate", "solarized_dark", "solarized_light", "terminal"
    ]
    
    # Ensure theme is valid
    if theme not in themes:
        theme = "monokai"
    
    try:
        content = st_ace(
            value=text,
            language=language.lower(),
            theme=theme,
            key=key,
            height=height,
            wrap=wrap,
            font_size=14,
            auto_update=auto_update,  # This prevents constant refresh
            # Editor options
            show_gutter=True,
            show_print_margin=True,
            annotations=None
        )
        
        return content if content is not None else text
        
    except Exception as e:
        # Fallback to text area if ACE fails
        st.warning(f"ACE editor failed ({str(e)}), using basic text area.")
        return _render_text_area_fallback(text, key, height)

def _render_text_area_fallback(text: str, key: str, height: int) -> str:
    """Render basic text area as fallback."""
    # Show info about the fallback only once
    if not ACE_AVAILABLE and key == "main_editor_json":  # Only show for main editor
        st.info(
            "💡 Install `streamlit-ace` for advanced editor features: "
            "`pip install streamlit-ace`"
        )
    
    content = st.text_area(
        label="Text Editor",
        value=text,
        height=height,
        key=key,
        help="Edit your text here. Install streamlit-ace for syntax highlighting.",
        label_visibility="collapsed"  # Hide the label since we have our own header
    )
    
    return content if content is not None else text

def get_editor_info() -> dict:
    """
    Get information about the available editor.
    
    Returns:
        Dictionary with editor information
    """
    return {
        "ace_available": ACE_AVAILABLE,
        "editor_type": "ACE Editor" if ACE_AVAILABLE else "Text Area",
        "features": {
            "syntax_highlighting": ACE_AVAILABLE,
            "line_numbers": ACE_AVAILABLE,
            "auto_completion": ACE_AVAILABLE,
            "themes": ACE_AVAILABLE,
            "search_replace": ACE_AVAILABLE,
            "code_folding": ACE_AVAILABLE
        }
    }

def render_editor_settings() -> dict:
    """
    Render editor settings in sidebar.
    
    Returns:
        Dictionary of current settings
    """
    settings = {}
    
    if ACE_AVAILABLE:
        st.sidebar.subheader("Editor Settings")
        
        # Theme selection
        themes = [
            "monokai", "github", "tomorrow", "kuroir", "twilight",
            "xcode", "textmate", "solarized_dark", "solarized_light"
        ]
        
        settings["theme"] = st.sidebar.selectbox(
            "Theme",
            themes,
            index=0,
            help="Choose editor color theme"
        )
        
        # Font size
        settings["font_size"] = st.sidebar.slider(
            "Font Size",
            min_value=10,
            max_value=20,
            value=14,
            help="Adjust editor font size"
        )
        
        # Line wrapping
        settings["wrap"] = st.sidebar.checkbox(
            "Wrap Lines",
            value=False,
            help="Enable line wrapping"
        )
        
        # Auto update - default to False to prevent refresh
        settings["auto_update"] = st.sidebar.checkbox(
            "Auto Update",
            value=False,
            help="Automatically update content on change (may cause refresh)"
        )
    
    else:
        settings = {
            "theme": "default",
            "font_size": 14,
            "wrap": False,
            "auto_update": False
        }
    
    return settings