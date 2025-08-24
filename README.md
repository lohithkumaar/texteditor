# Text Tools · JSON Validator · Formatter · Editor · Viewer

A production-ready Streamlit application for validating, formatting, editing, and viewing text files (JSON, TXT, MD) with an intuitive interface and powerful features.

## 🚀 Features

### General Text Editor
- **Multi-format Support**: Edit JSON, TXT, and Markdown files
- **Syntax Highlighting**: Language-specific highlighting with ACE integration
- **File Operations**: Upload files or paste content directly
- **Text Statistics**: Character, word, line, and paragraph counts
- **Undo Functionality**: 3-level undo stack for changes

### JSON-Specific Features
- **JSON Validation**: Syntax validation with detailed error reporting including line/column information and error context
- **Schema Validation**: Optional JSON Schema validation with path-based error reporting
- **JSON Formatting**: Format with customizable indentation (2, 4 spaces) and key sorting
- **JSON Minification**: Remove all unnecessary whitespace for compact JSON
- **Tree Viewer**: Expandable/collapsible JSON structure visualization

### Advanced Features
- **Validator Mode with Editor**: Dedicated editor in validator mode with validate button
- **Enhanced Diff Viewer**: Side-by-side and unified diff between original and edited content with manual input capability and change highlighting
- **Copy & Download**: Easy export of processed content in appropriate format
- **File Type Detection**: Automatic detection of content type

## 📋 Requirements

- Python 3.9+
- Streamlit 1.28.0+
- jsonschema 4.17.0+

### Optional Dependencies

- `streamlit-ace`: Enhanced code editor with syntax highlighting
- `ijson`: Streaming parser for large JSON files (>5MB)

## 🛠️ Installation

1. **Clone or create the project structure:**
```bash
mkdir text-tools-app
cd text-tools-app
```

2. **Create a virtual environment:**
```bash
python -m venv .venv
```

3. **Activate the virtual environment:**

On Windows:
```bash
.venv\Scripts\activate
```

On macOS/Linux:
```bash
source .venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## 🚀 Usage

### Running the Application

```bash
streamlit run app.py
```

The application will start and be available at `http://localhost:8501`

### Basic Workflow

1. **Input Content**: Upload a file (JSON/TXT/MD) or paste content in the sidebar
2. **Choose Mode**: Select from Editor, Viewer, Validator, or Diff mode
3. **Edit**: Use the syntax-highlighted editor to make changes
4. **Validate** (JSON only): Check syntax and optionally validate against a schema
5. **Format** (JSON only): Apply formatting with custom indentation and sorting
6. **View**: Explore content structure (JSON tree view for JSON files)
7. **Compare**: See differences between original and edited versions with enhanced diff viewer
8. **Export**: Download or copy the processed content

### Available Modes

- **Editor**: Universal text editor with syntax highlighting for JSON, Markdown, and plain text
- **Viewer**: Content viewer with JSON tree view for JSON files and rendered Markdown preview
- **Validator**: JSON validator with dedicated editor and validate button for detailed error reporting
- **Diff**: Compare original and modified versions with manual input capability and change highlighting

### File Type Support

- **JSON**: Full validation, formatting, schema validation, tree view
- **Markdown**: Syntax highlighting, preview rendering, text statistics
- **Plain Text**: Basic editing, text statistics, diff comparison

## 🔧 Key Changes Made

### Editor Mode
- ✅ Removed automatic JSON validation during editing
- ✅ Added support for TXT and MD files
- ✅ Language-specific syntax highlighting
- ✅ File type detection and appropriate handling
- ✅ Text statistics for non-JSON files

### Validator Mode
- ✅ Added dedicated editor within validator mode
- ✅ Added "Validate JSON" button that validates only when clicked
- ✅ Same detailed error reporting as before
- ✅ Copy from main editor functionality
- ✅ Separate text state for validator

### General Improvements
- ✅ Updated session state to handle multiple file types
- ✅ Enhanced file upload to support .txt and .md files
- ✅ Improved UI with file type indicators
- ✅ Better error handling for different content types

## 📁 Project Structure

```
text-tools-app/
├── app.py                 # Main Streamlit application (Updated)
├── requirements.txt       # Python dependencies
├── README.md             # This file (Updated)
├── src/                  # Source modules
│   ├── __init__.py
│   ├── config.py         # Configuration settings (Updated)
│   ├── editor.py         # Text editor component
│   ├── formatter.py      # JSON formatting functions
│   ├── validator.py      # JSON validation logic
│   ├── viewer.py         # Content viewer
│   └── utils.py          # Utility functions (Updated)
├── samples/              # Sample files
│   ├── valid.json        # Valid JSON example
│   ├── invalid.json      # Invalid JSON example
│   └── schema.json       # JSON Schema example
└── tests/                # Test files
    └── test_utils.py     # Unit tests
```

## 🧪 Testing

Run the tests using pytest:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest tests/ --cov=src
```

## 📝 Configuration

The application can be configured via `src/config.py`:

- `MAX_FILE_SIZE_MB`: Maximum file size for uploads (default: 5MB)
- `MAX_RECURSION_DEPTH`: Maximum depth for tree viewer (default: 8)
- `MAX_UNDO_STACK_SIZE`: Number of undo levels (default: 3)
- `SUPPORTED_EXTENSIONS`: List of supported file extensions
- `FILE_TYPE_MAPPINGS`: Language mappings for syntax highlighting

## 🔧 Advanced Features

### Universal Text Editor
- Support for JSON, Markdown, and plain text files
- Automatic file type detection
- Appropriate syntax highlighting for each file type
- File-type-specific actions and statistics

### Enhanced Validator Mode
- Dedicated JSON editor within validator mode
- Manual validation trigger via button click
- Detailed error reporting with line numbers and context
- Ability to copy content from main editor

### Multi-format Diff Viewer
- Works with any text format (JSON, MD, TXT)
- Side-by-side and unified diff views
- Manual input capability for both sides
- Color-coded change highlighting

### Smart File Handling
- Automatic content type detection
- Appropriate file extensions for downloads
- MIME type handling for different formats
- File statistics relevant to content type

## 🛠️ Troubleshooting

### Common Issues

1. **Import Error for streamlit-ace**
   - The app will fall back to a basic text area
   - Install with: `pip install streamlit-ace`

2. **Large File Performance**
   - Install `ijson` for streaming support: `pip install ijson`
   - Consider breaking large files into smaller chunks

3. **File Type Detection Issues**
   - App uses filename extension and content analysis
   - You can manually set file type if needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the error messages for specific guidance
3. File an issue with detailed error information and steps to reproduce

## 🔮 Future Enhancements

- Support for additional text formats (YAML, XML, CSV)
- Advanced text manipulation tools
- Multiple file comparison
- Export to different formats
- Dark/light theme toggle
- Collaborative editing features
- Integration with external APIs
- Plugin system for custom validators
