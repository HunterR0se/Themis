# Themis - Legal Document Analysis System

![Themis](images/themis_help.png)

Themis analyzes legal documents and generates defense strategies using Large Language Models.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/HunterR0se/Themis.git
cd Themis

# Create and activate virtual environment
python -m venv legalenv
source legalenv/bin/activate  # On Windows: .\legalenv\Scripts\activate

# Install dependencies
pip install PyPDF2 requests tqdm colorama

# Install OCR support (optional)
pip install pytesseract pdf2image pillow
# Plus system dependencies: tesseract-ocr and poppler-utils
```

### Basic Usage

1. **Put your case PDF documents in a directory**:

    ```
    ~/Legal/MyCase/*.pdf
    ```

2. **Run Themis**:

    ```bash
    # Full analysis and defense generation
    python themis.py full-process --case-dir ~/Legal/MyCase/

    # Or try with a specific model
    python themis.py full-process deepseek-r1 --case-dir ~/Legal/MyCase/

    # Or run on all available models to compare results
    python themis.py all-models --case-dir ~/Legal/MyCase/
    ```

3. **View results** in your case directory:
    - `YYYYMMDD_modelname.md` - Complete report
    - `YYYYMMDD_modelname/` - All detailed outputs

## Demo

[Watch the Themis Demo (Asciinema)](https://asciinema.org/a/MMJqpIhKKYTtEWw9OxRdZViAm)

## Example Outputs

- [SBF Analysis with Openthinker](example/sbf_full.md)
- [SBF Analysis with QwQ](example/sbf_qwq.md)
- [SBF Analysis with Initium/Law](example/sbf_initium_law.md)
- [SBF Analysis with Mistral](example/sbf_mistral.md)
- Many more in the `example` folder

## Core Commands

```bash
# Analyze documents
python themis.py analyze --dir ~/Legal/MyCase/

# Generate defense materials from analysis
python themis.py defend --case-dir ~/Legal/MyCase/

# Run full process (analysis + defense)
python themis.py full-process --case-dir ~/Legal/MyCase/

# Run with all available models
python themis.py all-models --case-dir ~/Legal/MyCase/
```

## Output Files

Themis creates:

1. **Document Analysis** - Questions and answers about each document
2. **Defense Strategy** - Legal strategy based on the analysis
3. **Action Items** - Tasks and next steps for the defense
4. **Case Timeline** - Chronological sequence of relevant events
5. **Combined Report** - All of the above in a single document

## Advanced Options

```bash
# Use a specific model
python themis.py full-process deepseek-r1 --case-dir ~/Legal/MyCase/

# Use custom questions
python themis.py analyze --dir ~/Legal/MyCase/ --questions my_questions.md

# Connect to a remote Ollama server
python themis.py --ollama-host 192.168.1.100 analyze --dir ~/Legal/MyCase/

# Compare specific models
python themis.py all-models --case-dir ~/Legal/MyCase/ --models llama3 mistral gpt-4o
```

---

## Detailed Information

<details>
<summary>Click to expand for more details</summary>

### Directory Structure

Themis organizes case files according to the following structure:

```
YOUR_CASE_DIR/                           # Your specified case directory
  ├── *.pdf                              # Source PDF documents
  ├── YYYYMMDD_modelname.md              # Combined report (when using full-process)
  ├── YYYYMMDD_modelname/                # Date and model-specific directory
  │   ├── case_analysis.log              # Analysis log file
  │   ├── analysis_cache.json            # Cache to speed up repeat runs
  │   ├── document_analysis_modelname.json   # Analysis results (JSON)
  │   ├── document_analysis_modelname.md     # Analysis results (readable)
  │   └── defense_materials/             # Generated defense materials
  │       ├── defense_strategy.md        # Defense strategy document
  │       ├── action_items.md            # Action items list
  │       └── case_timeline.md           # Case timeline
```

### Model Name Handling

When working with model names that contain slashes or other special characters (like "initium/law_model:latest"), Themis automatically sanitizes these names for use in filenames.

### OCR Support

Themis includes automatic OCR (Optical Character Recognition) for scanned PDFs when needed:

- Requires additional dependencies: `pytesseract`, `pdf2image`, and `poppler-utils`
- Automatically used when minimal text is detected in a PDF

### Caching System

Analysis results are cached to avoid re-analyzing documents unnecessarily. Each model has its own cache file.

### Batch Processing with Multiple Models

The `all-models` command runs Themis with multiple models sequentially:

```bash
python themis.py all-models --case-dir ~/Legal/MyCase/
```

This generates a comparison summary (`model_comparison_YYYYMMDD.md`) that links to all the outputs.

### Customizing Questions

You can create a custom questions file (markdown format) to guide the analysis:

```markdown
1. What are the central claims or charges against the defendant?
2. What key evidence is presented to support these allegations?
3. What are the legal issues identified in this document?
```

### Configuration

Themis maintains a configuration file at `~/.themis/themis.cfg` but you can override settings:

```bash
# Show current configuration
python themis.py config --show

# Reset to default configuration
python themis.py config --reset
```

</details>
