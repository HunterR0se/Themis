"""
Command handlers for the Themis CLI
"""
import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime
from colorama import Fore

from themis_lib.ui import print_status
from themis_lib.utils import check_ollama_connection, load_questions_from_file, generate_markdown_summary
from themis_lib.config import DEFAULT_QUESTIONS_FILE, FALLBACK_QUESTIONS
from themis_lib.analyzer import CaseAnalyzer
from themis_lib.defense import DefenseGenerator

def analyze_command(args):
    """Handle the analyze subcommand logic"""
    print_status(f"Legal Case Analysis", Fore.MAGENTA)
    print_status(f"===================", Fore.MAGENTA)
    
    # Check connection to Ollama server
    if not check_ollama_connection(args.ollama_api_url):
        print_status("Cannot proceed without connection to Ollama server", Fore.RED)
        return False
    
    # Initialize analyzer with specified model
    analyzer = CaseAnalyzer(args.dir, model=args.model, api_url=args.ollama_api_url)
    
    # Load questions
    if args.questions:
        questions = load_questions_from_file(args.questions)
        if not questions:
            # If questions file loading fails, use fallback questions
            questions = FALLBACK_QUESTIONS
    else:
        # Try loading from default questions file
        questions = load_questions_from_file(DEFAULT_QUESTIONS_FILE)
        if not questions:
            # If default questions file can't be loaded, use fallback questions
            questions = FALLBACK_QUESTIONS
        print_status(f"Using questions from {DEFAULT_QUESTIONS_FILE.name}", Fore.YELLOW)
    
    # Analyze all documents
    start_time = time.time()
    print_status("Beginning document analysis...", Fore.MAGENTA)
    results = analyzer.analyze_all_documents(args.questions, questions)
    
    if not results:
        print_status("No results were generated. Check for errors or lack of PDF files.", Fore.RED)
        return False
    
    # Calculate total time
    total_time = time.time() - start_time
    hours, remainder = divmod(total_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s" if hours else f"{int(minutes)}m {int(seconds)}s"
    
    # Save results with model name in filename
    output_file = analyzer.output_dir / f"document_analysis_{args.model}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    
    # Also save a copy in the case directory root for easy access
    case_output = Path(f"{args.dir}/document_analysis_{args.model}.json").expanduser()
    with open(case_output, 'w') as f:
        json.dump(results, f, indent=4)
    
    # Generate a human-readable markdown version
    md_output_file = analyzer.output_dir / f"document_analysis_{args.model}.md"
    md_case_output = Path(f"{args.dir}/document_analysis_{args.model}.md").expanduser()
    
    # Create the markdown summary
    generate_markdown_summary(results, args.model, md_output_file)
    # Also copy to the case directory root
    with open(md_output_file, 'r') as src, open(md_case_output, 'w') as dst:
        dst.write(src.read())
    
    print_status(f"Analysis complete in {time_str}!", Fore.GREEN)
    print_status(f"Analyzed {len(results)} documents", Fore.GREEN)
    print_status(f"Results saved to:", Fore.GREEN)
    print_status(f"  - {Fore.CYAN}{output_file}{Fore.GREEN} (JSON in log directory)", Fore.GREEN)
    print_status(f"  - {Fore.CYAN}{case_output}{Fore.GREEN} (JSON in case directory)", Fore.GREEN)
    print_status(f"  - {Fore.CYAN}{md_output_file}{Fore.GREEN} (Markdown in log directory)", Fore.GREEN)
    print_status(f"  - {Fore.CYAN}{md_case_output}{Fore.GREEN} (Markdown in case directory)", Fore.GREEN)
    
    analyzer.logger.info(f"Analysis complete. Results saved to {output_file} and {case_output}")
    return True

def defend_command(args):
    """Handle the defend subcommand logic"""
    print_status(f"Legal Defense Generator", Fore.MAGENTA)
    print_status(f"=====================", Fore.MAGENTA)
    
    # Check connection to Ollama server
    if not check_ollama_connection(args.ollama_api_url):
        print_status("Cannot proceed without connection to Ollama server", Fore.RED)
        return False
    
    try:
        # Initialize generator with the specified model
        generator = DefenseGenerator(args.case_dir, model=args.model, analysis_file=args.analysis, api_url=args.ollama_api_url)
        
        # Generate all defense materials
        materials = generator.generate_all_materials()
        
        # Display success message
        print_status("Defense generation completed successfully!", Fore.GREEN)
        print_status(f"Generated materials are available at:", Fore.GREEN)
        for name, path in materials.items():
            print_status(f"  - {name}: {Fore.CYAN}{path}{Fore.GREEN}", Fore.GREEN)
            
        return True
    except FileNotFoundError as e:
        print_status(f"Error: {e}", Fore.RED)
        print_status(f"Please run 'themis analyze' with model '{args.model}' first to generate the analysis file.", Fore.YELLOW)
        return False
    except Exception as e:
        print_status(f"Error during defense generation: {str(e)}", Fore.RED)
        return False

def full_process_command(args):
    """Handle the full-process subcommand logic - analyze then defend"""
    print_status(f"Legal Document Full Processing", Fore.MAGENTA)
    print_status(f"============================", Fore.MAGENTA)
    
    # Run analysis first
    analysis_args = argparse.Namespace(
        model=args.model,
        dir=args.case_dir,
        questions=args.questions,
        verbose=args.verbose,
        ollama_api_url=args.ollama_api_url  # Add this line
    )
    
    analysis_success = analyze_command(analysis_args)
    
    if not analysis_success:
        print_status("Analysis phase failed, cannot proceed to defense generation", Fore.RED)
        return False
    
    # Then run defense generation
    defense_args = argparse.Namespace(
        model=args.model,
        case_dir=args.case_dir,
        analysis=None,  # Use the default analysis file based on model
        ollama_api_url=args.ollama_api_url  # Add this line
    )
    
    defense_success = defend_command(defense_args)
    
    if not defense_success:
        print_status("Defense generation phase failed", Fore.RED)
        return False
    
    print_status("Full processing completed successfully!", Fore.GREEN)
    return True