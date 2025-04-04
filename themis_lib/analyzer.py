"""
CaseAnalyzer class for analyzing legal documents
"""
import json
from pathlib import Path
import time
from datetime import datetime
import logging
from colorama import Fore

from themis_lib.ui import print_status
from themis_lib.config import DEFAULT_MODEL, DEFAULT_QUESTIONS_FILE, FALLBACK_QUESTIONS
from themis_lib.utils import (
    load_questions_from_file, 
    extract_text_from_pdf, 
    query_ollama, 
    setup_logging,
    sanitize_model_name
)

class CaseAnalyzer:
    """Analyzes legal case documents by extracting text and querying LLMs"""
    
    def __init__(self, case_dir, model=DEFAULT_MODEL, api_url=None, run_dir=None):
        self.case_dir = Path(case_dir).expanduser()
        self.model = model
        self.sanitized_model = sanitize_model_name(model)
        self.api_url = api_url
        
        # Use the provided run directory or create a new one
        if run_dir:
            self.output_dir = Path(run_dir)
        else:
            # Create a date and model-specific directory in the case directory
            date_str = datetime.now().strftime('%Y%m%d')
            self.output_dir = self.case_dir / f"{date_str}_{self.sanitized_model}"
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache files are stored in the output directory
        self.analysis_cache = {}
        self.cache_file = self.output_dir / "analysis_cache.json"

        # Set up logging
        self.log_path = self.output_dir / "case_analysis.log"
        self.logger = setup_logging(self.log_path, f'analyzer_{self.model}')

        print_status(f"Initializing analyzer with model: {Fore.CYAN}{model}{Fore.GREEN}", Fore.GREEN)
        print_status(f"Case directory: {Fore.CYAN}{self.case_dir}{Fore.GREEN}", Fore.GREEN)
        print_status(f"Using output directory: {Fore.CYAN}{self.output_dir}{Fore.GREEN}", Fore.GREEN)

        self.load_cache()
        
    def load_cache(self):
        """Load previous analysis results if they exist"""
        if self.cache_file.exists():
            print_status(f"Loading cache from {self.cache_file}", Fore.GREEN)
            with open(self.cache_file, 'r') as f:
                self.analysis_cache = json.load(f)
                print_status(f"Loaded {len(self.analysis_cache)} cached analyses", Fore.GREEN)
        else:
            print_status("No cache file found, starting fresh", Fore.YELLOW)
                
    def save_cache(self):
        """Save analysis results to cache"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.analysis_cache, f, indent=4)
        print_status(f"Saved {len(self.analysis_cache)} analyses to cache", Fore.GREEN)

    def analyze_document(self, pdf_path, questions_file=None):
        """Analyze a single document with specific questions"""
        # Load questions from file if provided (reload every time to catch changes)
        if questions_file and Path(questions_file).exists():
            questions = load_questions_from_file(questions_file)
            if not questions:
                # Fall back to default questions if loading fails
                questions = self.default_questions
        else:
            questions = self.default_questions
            
        file_hash = f"{pdf_path}_{hash(str(questions))}"
        
        if file_hash in self.analysis_cache:
            print_status(f"Using cached analysis for {Fore.CYAN}{pdf_path.name}{Fore.GREEN}", Fore.GREEN)
            return self.analysis_cache[file_hash]

        print_status(f"Analyzing {Fore.CYAN}{pdf_path.name}{Fore.MAGENTA}...", Fore.MAGENTA)
        text = extract_text_from_pdf(pdf_path)
        
        if not text:
            print_status(f"No text could be extracted from {pdf_path.name}", Fore.RED)
            return {"filename": pdf_path.name, "analysis": {q: "" for q in questions}}
        
        results = {
            "filename": pdf_path.name,
            "analysis": {}
        }

        for i, question in enumerate(questions, 1):
            print_status(f"Question {i}/{len(questions)}: {question[:40]}...", Fore.YELLOW)
            
            prompt = f"""
            Based on the following legal document, please answer this question:
            {question}
            
            Document text:
            {text[:4000]}  # Using first 4000 chars to avoid token limits
            """
            
            answer = query_ollama(self.model, prompt, pdf_path.name, self.logger, self.api_url)
            results["analysis"][question] = answer
            
            # Print a short preview of the answer
            preview = answer[:100].replace('\n', ' ') + ('...' if len(answer) > 100 else '')
            print_status(f"Answer: {preview}", Fore.CYAN)

        self.analysis_cache[file_hash] = results
        self.save_cache()
        print_status(f"Completed analysis of {Fore.CYAN}{pdf_path.name}{Fore.GREEN}", Fore.GREEN)
        return results

    def analyze_all_documents(self, questions_file=None, default_questions=None):
        """Analyze all PDF documents in the case directory"""
        # If no default_questions provided, attempt to load from DEFAULT_QUESTIONS_FILE
        if not default_questions:
            default_questions = load_questions_from_file(DEFAULT_QUESTIONS_FILE)
            if not default_questions:
                default_questions = FALLBACK_QUESTIONS
        
        # Store default questions for use in analyze_document
        self.default_questions = default_questions
        
        results = []
        pdf_files = sorted([f for f in self.case_dir.glob("*.pdf")])
        
        if not pdf_files:
            print_status(f"No PDF files found in {self.case_dir}", Fore.RED)
            return results
            
        print_status(f"Found {len(pdf_files)} PDF documents to analyze", Fore.GREEN)
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print_status(f"Processing document {i}/{len(pdf_files)}: {pdf_file.name}", Fore.MAGENTA)
            analysis = self.analyze_document(pdf_file, questions_file)
            results.append(analysis)
            print_status(f"Completed {i}/{len(pdf_files)} documents", Fore.GREEN)
            
        return results