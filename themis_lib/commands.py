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
from themis_lib.utils import (
    check_ollama_connection, 
    load_questions_from_file, 
    generate_markdown_summary,
    sanitize_model_name
)
from themis_lib.config import DEFAULT_QUESTIONS_FILE, FALLBACK_QUESTIONS
from themis_lib.analyzer import CaseAnalyzer
from themis_lib.defense import DefenseGenerator
from themis_lib.document import combine_documents

def analyze_command(args):
    """Handle the analyze subcommand logic"""
    print_status(f"Legal Case Analysis", Fore.MAGENTA)
    print_status(f"===================", Fore.MAGENTA)
    
    # Check connection to Ollama server
    if not check_ollama_connection(args.ollama_api_url):
        print_status("Cannot proceed without connection to Ollama server", Fore.RED)
        return False
    
    # Sanitize model name for use in filenames
    sanitized_model = sanitize_model_name(args.model)
    
    # Determine output directory
    if hasattr(args, 'run_dir'):
        # Use the provided run directory (for full-process command)
        run_dir = args.run_dir
    else:
        # Create a new run directory (for standalone analyze command)
        date_str = datetime.now().strftime('%Y%m%d')
        run_dir = Path(args.dir) / f"{date_str}_{sanitized_model}"
        run_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize analyzer with specified model and run directory
    analyzer = CaseAnalyzer(args.dir, model=args.model, api_url=args.ollama_api_url, run_dir=run_dir)
    
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
    
    # Save results with model name in filename (in the run directory)
    output_file = run_dir / f"document_analysis_{sanitized_model}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    
    # Generate a human-readable markdown version (in the run directory)
    md_output_file = run_dir / f"document_analysis_{sanitized_model}.md"
    
    # Create the markdown summary
    generate_markdown_summary(results, args.model, md_output_file)
    
    print_status(f"Analysis complete in {time_str}!", Fore.GREEN)
    print_status(f"Analyzed {len(results)} documents", Fore.GREEN)
    print_status(f"Results saved to:", Fore.GREEN)
    print_status(f"  - {Fore.CYAN}{output_file}{Fore.GREEN} (JSON)", Fore.GREEN)
    print_status(f"  - {Fore.CYAN}{md_output_file}{Fore.GREEN} (Markdown)", Fore.GREEN)
    
    analyzer.logger.info(f"Analysis complete. Results saved to {output_file}")
    return True

def defend_command(args):
    """Handle the defend subcommand logic"""
    print_status(f"Legal Defense Generator", Fore.MAGENTA)
    print_status(f"=====================", Fore.MAGENTA)
    
    # Check connection to Ollama server
    if not check_ollama_connection(args.ollama_api_url):
        print_status("Cannot proceed without connection to Ollama server", Fore.RED)
        return False
    
    # Sanitize model name for use in filenames
    sanitized_model = sanitize_model_name(args.model)
    
    # Determine output directory
    if hasattr(args, 'run_dir'):
        # Use the provided run directory (for full-process command)
        run_dir = args.run_dir
    else:
        # Create a new run directory (for standalone defend command)
        date_str = datetime.now().strftime('%Y%m%d')
        run_dir = Path(args.case_dir) / f"{date_str}_{sanitized_model}"
        run_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Determine the analysis file to use
        if args.analysis:
            # Use the specified analysis file
            analysis_file = Path(args.analysis).expanduser()
        else:
            # Check both locations for the analysis file - run directory and case directory
            run_dir_analysis = run_dir / f"document_analysis_{sanitized_model}.json"
            case_dir_analysis = Path(args.case_dir) / f"document_analysis_{sanitized_model}.json"
            
            if run_dir_analysis.exists():
                analysis_file = run_dir_analysis
            elif case_dir_analysis.exists():
                analysis_file = case_dir_analysis
            else:
                raise FileNotFoundError(f"Analysis file not found in {run_dir} or {args.case_dir}")
        
        # Initialize generator with the specified model and run directory
        generator = DefenseGenerator(args.case_dir, model=args.model, 
                                    analysis_file=analysis_file, 
                                    api_url=args.ollama_api_url,
                                    run_dir=run_dir)
        
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
    
    case_dir = args.case_dir
    model = args.model
    sanitized_model = sanitize_model_name(model)
    date_str = datetime.now().strftime('%Y%m%d')
    
    # Create the date and model-specific directory that will contain all outputs
    run_dir = Path(case_dir) / f"{date_str}_{sanitized_model}"
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Run analysis first
    analysis_args = argparse.Namespace(
        model=model,
        dir=case_dir,
        questions=args.questions,
        verbose=args.verbose,
        ollama_api_url=args.ollama_api_url,
        run_dir=run_dir  # Pass the run directory
    )
    
    analysis_success = analyze_command(analysis_args)
    
    if not analysis_success:
        print_status("Analysis phase failed, cannot proceed to defense generation", Fore.RED)
        return False
    
    # Then run defense generation
    defense_args = argparse.Namespace(
        model=model,
        case_dir=case_dir,
        analysis=None,  # Use the default analysis file based on model
        ollama_api_url=args.ollama_api_url,
        run_dir=run_dir  # Pass the run directory
    )
    
    defense_success = defend_command(defense_args)
    
    if not defense_success:
        print_status("Defense generation phase failed", Fore.RED)
        return False
    
    # Create a combined document with all outputs
    try:
        # Paths to all the generated files
        defense_dir = run_dir / "defense_materials"
        
        analysis_md_path = run_dir / f"document_analysis_{sanitized_model}.md"
        defense_strategy_path = defense_dir / "defense_strategy.md"
        action_items_path = defense_dir / "action_items.md"
        timeline_path = defense_dir / "case_timeline.md"
        
        # Create combined document in the case directory (not in run_dir)
        combined_filename = f"{date_str}_{sanitized_model}.md"
        combined_path = Path(case_dir) / combined_filename
        
        combine_documents(
            case_dir=case_dir,
            model_name=model,
            analysis_md_path=analysis_md_path,
            defense_strategy_path=defense_strategy_path,
            action_items_path=action_items_path,
            timeline_path=timeline_path,
            output_path=combined_path
        )
        
        print_status(f"Combined document created: {Fore.CYAN}{combined_path}{Fore.GREEN}", Fore.GREEN)
    except Exception as e:
        print_status(f"Warning: Could not create combined document: {str(e)}", Fore.YELLOW)
        print_status("Individual documents are still available", Fore.YELLOW)
    
    print_status("Full processing completed successfully!", Fore.GREEN)
    return True