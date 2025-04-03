"""
Utilities for document handling, loading questions, and Ollama API interaction.
"""
import re
import PyPDF2
import requests
import json
import time
import logging 
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
from colorama import Fore, Style

from themis_lib.ui import print_status
from themis_lib.config import DEFAULT_QUESTIONS_FILE, FALLBACK_QUESTIONS, OLLAMA_API_URL

def setup_logging(log_path, logger_name):
    """Setup logging with a specific logger name"""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    
    # Create handler
    file_handler = logging.FileHandler(log_path)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)
    print_status(f"Logging to file: {Fore.CYAN}{log_path}{Fore.GREEN}", Fore.GREEN)
    return logger

def load_questions_from_file(file_path):
    """Load questions from a markdown file
    
    The file should contain numbered questions, one per line.
    Lines not starting with a number followed by a period are ignored.
    """
    questions = []
    try:
        with open(file_path, 'r') as f:
            content = f.readlines()
        
        # Extract questions (lines starting with a number and period)
        for line in content:
            line = line.strip()
            # Match lines starting with a number followed by a period or parenthesis
            if re.match(r'^\d+[\.\)]', line):
                # Remove the number and any leading spaces
                question = re.sub(r'^\d+[\.\)]\s*', '', line)
                questions.append(question)
        
        print_status(f"Loaded {len(questions)} questions from {file_path}", Fore.GREEN)
        return questions
    except FileNotFoundError:
        print_status(f"Questions file not found: {Fore.CYAN}{file_path}{Fore.RED}", Fore.RED)
        print_status("Using default questions instead", Fore.YELLOW)
        return None
    except Exception as e:
        print_status(f"Error loading questions: {str(e)}", Fore.RED)
        return None

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    try:
        print_status(f"Extracting text from {Fore.CYAN}{pdf_path.name}{Fore.YELLOW}...", Fore.YELLOW)
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            pages = len(reader.pages)
            for i, page in enumerate(tqdm(reader.pages, desc="Extracting Pages", unit="page")):
                text += page.extract_text() + "\n"
            print_status(f"Extracted {pages} pages ({len(text)} characters) from {pdf_path.name}", Fore.GREEN)
            return text
    except Exception as e:
        print_status(f"Error extracting text from {pdf_path.name}: {str(e)}", Fore.RED)
        return ""

def check_ollama_connection(api_url=None):
    """Check if we can connect to the Ollama server and get available models"""
    if api_url is None:
        from themis_lib.config import OLLAMA_API_URL
        api_url = OLLAMA_API_URL
        
    try:
        host_port = api_url.split("/api/")[0]
        print_status(f"Connecting to Ollama server at {host_port}...", Fore.YELLOW)
        response = requests.get(api_url.replace('/api/generate', '/api/version'))
        if response.status_code == 200:
            version = response.json().get('version', 'unknown')
            print_status(f"Connected to Ollama server version {version}", Fore.GREEN)
            
            # Get available models
            models_resp = requests.get(api_url.replace('/api/generate', '/api/tags'))
            if models_resp.status_code == 200:
                models = [m['name'] for m in models_resp.json().get('models', [])]
                print_status(f"Available models: {', '.join(models[:5])}{'...' if len(models) > 5 else ''}", Fore.GREEN)
            return True
        else:
            print_status(f"Failed to connect to Ollama server: {response.text}", Fore.RED)
            return False
    except Exception as e:
        print_status(f"Error connecting to Ollama server: {str(e)}", Fore.RED)
        return False

def query_ollama(model, prompt, task_name="task", logger=None, api_url=None):
    """Query Ollama API with a prompt"""
    if api_url is None:
        from themis_lib.config import OLLAMA_API_URL
        api_url = OLLAMA_API_URL
        
    try:
        print_status(f"Querying Ollama ({Fore.CYAN}{model}{Fore.YELLOW}) for {Fore.CYAN}{task_name}{Fore.YELLOW}...", Fore.YELLOW)
        start_time = time.time()
        
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
            
        response = requests.post(api_url, json=data)
        
        if response.status_code == 200 and 'response' in response.json():
            elapsed = time.time() - start_time
            result = response.json()['response']
            print_status(f"Got response for {task_name} ({len(result)} chars) in {elapsed:.2f}s", Fore.GREEN)
            # Print preview of response
            preview = result[:100].replace('\n', ' ') + ('...' if len(result) > 100 else '')
            print_status(f"Preview: {Fore.CYAN}{preview}{Fore.GREEN}", Fore.GREEN)
            return result
        else:
            error_msg = f"Unexpected response format: {response.text}"
            print_status(f"Error from Ollama: {response.text}", Fore.RED)
            if logger:
                logger.error(error_msg)
            return ""
    except Exception as e:
        error_msg = f"Error querying Ollama: {str(e)}"
        print_status(error_msg, Fore.RED)
        if logger:
            logger.error(error_msg)
        return ""

def generate_markdown_summary(results, model_name, output_path):
    """
    Generate a human-readable Markdown summary of the analysis results
    
    Args:
        results: List of document analysis results
        model_name: Name of the model used for analysis
        output_path: Where to save the Markdown file
    """
    if not results:
        print_status("No results to summarize", Fore.YELLOW)
        return
        
    print_status(f"Generating human-readable summary of {len(results)} documents...", Fore.MAGENTA)

    with open(output_path, 'w') as f:
        # Write header
        f.write(f"# Document Analysis Summary\n\n")
        f.write(f"*Generated by Themis using the {model_name} model on {datetime.now().strftime('%Y-%m-%d at %H:%M')}*\n\n")
        f.write("## Overview\n\n")
        
        # Write document list
        f.write("### Analyzed Documents\n\n")
        for i, doc in enumerate(results, 1):
            f.write(f"{i}. **{doc['filename']}**\n")
        f.write("\n")
        
        # Write detailed analysis for each document
        f.write("## Document Details\n\n")
        
        for doc in results:
            f.write(f"### {doc['filename']}\n\n")
            
            # Create a table of contents for this document
            f.write("**Quick Links:**\n\n")
            for i, (question, _) in enumerate(doc['analysis'].items(), 1):
                # Create a section ID from the question (lowercase, spaces to dashes)
                section_id = question.lower().replace(' ', '-').replace('?', '').replace(',', '')[:30]
                f.write(f"- [{i}. {question}](#{section_id})\n")
            f.write("\n")
            
            # Write each Q&A pair
            for question, answer in doc['analysis'].items():
                section_id = question.lower().replace(' ', '-').replace('?', '').replace(',', '')[:30]
                f.write(f"<a id='{section_id}'></a>\n") 
                f.write(f"#### {question}\n\n")
                f.write(f"{answer}\n\n")
                f.write("---\n\n")
                
        # Add footer
        f.write("\n\n*End of Document Analysis Summary*\n")
    
    print_status(f"Summary saved to {output_path}", Fore.GREEN)
    return output_path