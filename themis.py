#!/usr/bin/env python3
"""
Themis - Legal Document Analysis and Defense Generation System

A comprehensive system for analyzing legal case documents and generating
defense materials using Large Language Models (LLMs) via Ollama.

This module provides functionality to:
1. Extract text from PDF legal documents
2. Analyze documents by asking a series of legal questions
3. Generate defense strategies, action items, and case timelines
4. Maintain organized logs and caching of results
"""

import argparse
import sys
from colorama import init
from pathlib import Path

# Initialize colorama
init()

# Import from themis_lib package
from themis_lib.ui import print_colorful_help
from themis_lib.config import (
    DEFAULT_MODEL, 
    DEFAULT_OLLAMA_HOST, 
    DEFAULT_OLLAMA_PORT,
    get_config,
    save_config
)
from themis_lib.commands import (
    analyze_command,
    defend_command,
    full_process_command
)

def main():
    """Main entry point for the Themis application"""
    # Get saved configuration
    config = get_config()
    
    # Create top-level parser
    parser = argparse.ArgumentParser(
        description='Themis - Legal Document Analysis and Defense Generation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze documents in a specific case directory:
  themis analyze --dir ~/Legal/MyCase/
  
  # Generate defense materials for an analyzed case:
  themis defend --case-dir ~/Legal/MyCase/
  
  # Run the full process (analysis + defense) with a specific model:
  themis full-process deepseek-r1 --case-dir ~/Legal/MyCase/
  
  # Analyze with custom questions file:
  themis analyze --dir ~/Legal/MyCase/ --questions my_questions.md
  
  # Generate defense using a specific analysis file:
  themis defend --case-dir ~/Legal/MyCase/ --analysis ~/path/to/specific_analysis.json
  
  # Connect to a remote Ollama server:
  themis analyze --ollama-host 192.168.1.100 --dir ~/Legal/MyCase/
        """
    )
    
    # Add model argument to top-level parser and set DEFAULT_MODEL
    parser.add_argument('--model', dest='default_model', 
                      default=config["model"],
                      help=f'Ollama model to use (default: {config["model"]})')
    
    # Add Ollama connection arguments
    parser.add_argument('--ollama-host', dest='ollama_host',
                       default=config["ollama_host"],
                       help=f'Ollama server hostname or IP (default: {config["ollama_host"]})')
    parser.add_argument('--ollama-port', dest='ollama_port', type=int,
                       default=config["ollama_port"],
                       help=f'Ollama server port (default: {config["ollama_port"]})')
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Sub-commands')
    
    # Create parser for "analyze" command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze legal documents')
    analyze_parser.add_argument('model', nargs='?', default=argparse.SUPPRESS,
                              help=f'Ollama model to use (default: from --model or {config["model"]})')
    analyze_parser.add_argument('--dir', '-d', required=True,
                              help='Directory containing PDF documents (REQUIRED)')
    analyze_parser.add_argument('--questions', '-q', default=None,
                              help='Path to markdown file with questions (default: questions.md in current directory)')
    analyze_parser.add_argument('--verbose', '-v', action='store_true',
                              help='Enable verbose output')
    analyze_parser.set_defaults(func=analyze_command)
    
    # Create parser for "defend" command
    defend_parser = subparsers.add_parser('defend', help='Generate defense materials')
    defend_parser.add_argument('model', nargs='?', default=argparse.SUPPRESS,
                             help=f'Ollama model to use (default: from --model or {config["model"]})')
    defend_parser.add_argument('--case-dir', '-d', required=True,
                             help='Directory containing case documents (REQUIRED)')
    defend_parser.add_argument('--analysis', '-a', 
                             help='Path to specific analysis file (optional)')
    defend_parser.set_defaults(func=defend_command)
    
    # Create parser for "full-process" command
    full_process_parser = subparsers.add_parser('full-process', help='Run analysis and defense generation in sequence')
    full_process_parser.add_argument('model', nargs='?', default=argparse.SUPPRESS,
                                   help=f'Ollama model to use (default: from --model or {config["model"]})')
    full_process_parser.add_argument('--case-dir', '-d', required=True,
                                   help='Directory containing case documents (REQUIRED)')
    full_process_parser.add_argument('--questions', '-q', default=None,
                                   help='Path to markdown file with questions (for analysis phase)')
    full_process_parser.add_argument('--verbose', '-v', action='store_true',
                                   help='Enable verbose output')
    full_process_parser.set_defaults(func=full_process_command)
    
    # Create parser for "config" command
    config_parser = subparsers.add_parser('config', help='Show or modify configuration')
    config_parser.add_argument('--show', action='store_true',
                              help='Show current configuration')
    config_parser.add_argument('--reset', action='store_true',
                              help='Reset configuration to defaults')
    config_parser.set_defaults(func=config_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Build Ollama API URL from host and port if provided
    if hasattr(args, 'ollama_host') or hasattr(args, 'ollama_port'):
        host = getattr(args, 'ollama_host', DEFAULT_OLLAMA_HOST)
        port = getattr(args, 'ollama_port', DEFAULT_OLLAMA_PORT)
        args.ollama_api_url = f"http://{host}:{port}/api/generate"
    else:
        args.ollama_api_url = config["ollama_api_url"]
    
    # Set the model from the default_model if not specified in subcommand
    if not hasattr(args, 'model') and hasattr(args, 'default_model'):
        args.model = args.default_model
    
    # Save current configuration (except for show/reset config command)
    if not (hasattr(args, 'func') and args.func == config_command and (args.show or args.reset)):
        # Update config with current settings
        config.update({
            "model": args.model,
            "ollama_host": getattr(args, 'ollama_host', DEFAULT_OLLAMA_HOST),
            "ollama_port": getattr(args, 'ollama_port', DEFAULT_OLLAMA_PORT),
            "ollama_api_url": args.ollama_api_url
        })
        
        # Update last_case_dir if available
        if hasattr(args, 'dir'):
            config["last_case_dir"] = args.dir
        elif hasattr(args, 'case_dir'):
            config["last_case_dir"] = args.case_dir
        
        # Save updated configuration
        save_config(config)
        
    # Call the appropriate function based on the command
    if hasattr(args, 'func'):
        try:
            success = args.func(args)
            sys.exit(0 if success else 1)
        except KeyboardInterrupt:
            print("\nOperation interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    else:
        print_colorful_help()
        sys.exit(0)

def config_command(args):
    """Handle the config subcommand logic"""
    if args.show:
        config = get_config()
        print("\nCurrent Configuration:")
        print("----------------------")
        for key, value in config.items():
            print(f"{key}: {value}")
        print()
        return True
    
    if args.reset:
        config = {
            "model": DEFAULT_MODEL,
            "ollama_host": DEFAULT_OLLAMA_HOST,
            "ollama_port": DEFAULT_OLLAMA_PORT,
            "ollama_api_url": f"http://{DEFAULT_OLLAMA_HOST}:{DEFAULT_OLLAMA_PORT}/api/generate",
            "last_case_dir": ""
        }
        save_config(config)
        print("\nConfiguration has been reset to defaults.")
        return True
        
    return False


if __name__ == "__main__":
    main()