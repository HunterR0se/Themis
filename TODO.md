# Themis Development TODO

## Project Overview

Themis is a legal document analysis and defense generation system that uses LLMs via Ollama to:
1. Extract and analyze text from legal PDFs 
2. Generate comprehensive defense materials

### Current State

- **Architecture**: Modular Python package with themis.py at the root and themis_lib modules
- **Features**:
  - Document analysis with customizable questions
  - Defense material generation (strategy, action items, timeline)
  - Both JSON and human-readable Markdown output
  - Automatic OCR for scanned documents
  - Configuration file system (~/.themis/themis.cfg)
  - Remote Ollama server support
- **Directory Structure**:
  - themis.py - Main entry point script
  - themis_lib/ - Package with all modules
    - analyzer.py - Document analysis functionality
    - commands.py - Command-line interface handlers
    - config.py - Configuration management
    - defense.py - Defense generation functionality
    - ui.py - User interface elements (colorful output)
    - utils.py - Utility functions

### Development Environment

- **Dependencies**:
  - Core: PyPDF2, requests, tqdm, colorama
  - OCR (optional): pytesseract, pdf2image, pillow
  - System (for OCR): tesseract-ocr, poppler-utils
- **Virtual Environment**:
  - Created with `python -m venv legalenv`
  - Activated with `source legalenv/bin/activate`

### Ollama Configuration

- Default Ollama server: localhost:11434
- Remote server configuration:
  - Command line: `--ollama-host` and `--ollama-port` options
  - Configuration file: Automatically saved in ~/.themis/themis.cfg
- Models: Uses mistral as default, but any model available in Ollama can be used

## Current Issues and Limitations

1. **Scanned PDFs**: While automatic OCR has been implemented, it requires system dependencies (tesseract-ocr & poppler-utils)
2. **Token Limits**: For large documents, only the first portion of text is used due to LLM token limits
3. **Local File Access Only**: Currently works with local files, no web API or browser interface

## Next Development Steps

### High Priority

1. **Testing Framework**
   - Add unit tests for all modules
   - Create integration tests with sample PDFs
   - Implement CI/CD pipeline

2. **Error Handling**
   - Improve error messages and recovery mechanisms
   - Add comprehensive logging throughout the application
   - Implement retry logic for LLM API failures

3. **Performance Optimization**
   - Add multi-threading for processing multiple documents
   - Implement chunking for large documents (to avoid token limits)
   - Optimize OCR performance for large PDFs

### Medium Priority

1. **Web Interface**
   - Create simple Flask/FastAPI web application
   - Upload interface for documents
   - Progress tracking and result viewing

2. **LLM Provider Options**
   - Support for OpenAI, Anthropic, and other providers
   - Configurable provider switching
   - Model comparison tools

3. **Document Management**
   - Case management with multiple related documents
   - Document categorization and tagging
   - Search functionality within analyses

### Lower Priority

1. **User Management**
   - Multi-user support with authentication
   - User-specific configurations and histories
   - Collaboration features

2. **Export Options**
   - PDF export of generated defense materials
   - Customizable templates for outputs
   - Email/sharing options

## Getting Started for New Developers

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/Themis.git
   cd Themis
   ```

2. **Set Up Environment**
   ```bash
   python -m venv legalenv
   source legalenv/bin/activate  # On Windows: legalenv\Scripts\activate
   pip install -e .  # Install in development mode
   ```

3. **Run with Sample Data**
   ```bash
   # Create a test directory with PDFs
   mkdir -p test_case
   cp /path/to/sample/legaldocs/*.pdf test_case/
   
   # Run analysis
   python themis.py analyze --dir test_case
   ```

4. **For OCR Support** (optional)
   ```bash
   # System dependencies
   sudo apt-get install tesseract-ocr poppler-utils  # Debian/Ubuntu
   brew install tesseract poppler  # macOS
   
   # Python packages
   pip install pytesseract pdf2image pillow
   ```

## Code Structure and Entry Points

- **Main Entry Point**: `main()` in themis.py
- **Analysis Process**: `analyze_command()` in themis_lib/commands.py
- **Defense Generation**: `defend_command()` in themis_lib/commands.py
- **Text Extraction**: `extract_text_from_pdf()` in themis_lib/utils.py
- **LLM Interaction**: `query_ollama()` in themis_lib/utils.py
- **Configuration**: `get_config()` and `save_config()` in themis_lib/config.py

## Command Reference

```bash
# Basic usage
python themis.py analyze --dir CASE_DIR
python themis.py defend --case-dir CASE_DIR
python themis.py full-process --case-dir CASE_DIR

# With model specified
python themis.py analyze mistral --dir CASE_DIR
python themis.py analyze deepseek-r1 --dir CASE_DIR

# Remote Ollama server
python themis.py --ollama-host 192.168.0.50 analyze --dir CASE_DIR

# Configuration
python themis.py config --show
python themis.py config --reset
```

## Implementation Notes

- The analysis cache is per-model and stored in the model-specific directory
- Questions are reloaded before each document to allow on-the-fly customization
- OCR is automatically attempted for PDFs with minimal extractable text
- A human-readable markdown summary is generated alongside the JSON analysis