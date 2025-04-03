"""
UI and display utilities for Themis.
"""
import time
from datetime import datetime
from colorama import Fore, Style

def print_colorful_help():
    """Print a colorful help message with Themis banner"""
    banner = f"""
{Fore.CYAN}████████╗██╗  ██╗███████╗███╗   ███╗██╗███████╗
╚══██╔══╝██║  ██║██╔════╝████╗ ████║██║██╔════╝
   ██║   ███████║█████╗  ██╔████╔██║██║███████╗
   ██║   ██╔══██║██╔══╝  ██║╚██╔╝██║██║╚════██║
   ██║   ██║  ██║███████╗██║ ╚═╝ ██║██║███████║
   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝╚══════╝{Style.RESET_ALL}
{Fore.GREEN}Legal Document Analysis & Defense Generation System{Style.RESET_ALL}
"""
    
    usage = f"""
{Fore.YELLOW}USAGE:{Style.RESET_ALL} {Fore.CYAN}python themis.py{Style.RESET_ALL} {Fore.MAGENTA}command{Style.RESET_ALL} [{Fore.GREEN}model{Style.RESET_ALL}] [options]

{Fore.YELLOW}COMMANDS:{Style.RESET_ALL}
  {Fore.MAGENTA}analyze{Style.RESET_ALL}       Analyze legal documents using an LLM
  {Fore.MAGENTA}defend{Style.RESET_ALL}        Generate defense materials from analysis
  {Fore.MAGENTA}full-process{Style.RESET_ALL}  Run both analysis and defense generation
  
{Fore.YELLOW}COMMONLY USED OPTIONS:{Style.RESET_ALL}
  {Fore.GREEN}--dir{Style.RESET_ALL}, {Fore.GREEN}-d{Style.RESET_ALL}          Directory with PDF documents (for analyze)
  {Fore.GREEN}--case-dir{Style.RESET_ALL}, {Fore.GREEN}-d{Style.RESET_ALL}     Directory with case documents (for defend/full-process)
  {Fore.GREEN}--questions{Style.RESET_ALL}, {Fore.GREEN}-q{Style.RESET_ALL}    Custom questions file (default: questions.md)
  {Fore.GREEN}--analysis{Style.RESET_ALL}, {Fore.GREEN}-a{Style.RESET_ALL}     Specific analysis file (for defend)
  {Fore.GREEN}--verbose{Style.RESET_ALL}, {Fore.GREEN}-v{Style.RESET_ALL}      Enable verbose output
  
{Fore.YELLOW}EXAMPLES:{Style.RESET_ALL}
  # Analyze documents in a case directory:
  {Fore.CYAN}python themis.py analyze{Style.RESET_ALL} --dir ~/Cases/Smith
  
  # Generate defense with DeepSeek model:
  {Fore.CYAN}python themis.py{Style.RESET_ALL} {Fore.MAGENTA}defend{Style.RESET_ALL} {Fore.GREEN}deepseek-r1{Style.RESET_ALL} {Fore.CYAN}--case-dir{Style.RESET_ALL} ~/Cases/Johnson
  
  # Run full process with custom questions:
  {Fore.CYAN}python themis.py full-process{Style.RESET_ALL} --case-dir ~/Cases/Davis {Fore.GREEN}--questions{Style.RESET_ALL} my_questions.md
  
{Fore.YELLOW}FOR MORE DETAILS:{Style.RESET_ALL}
  {Fore.CYAN}python themis.py{Style.RESET_ALL} {Fore.MAGENTA}analyze{Style.RESET_ALL} --help
  {Fore.CYAN}python themis.py{Style.RESET_ALL} {Fore.MAGENTA}defend{Style.RESET_ALL} --help
  {Fore.CYAN}python themis.py{Style.RESET_ALL} {Fore.MAGENTA}full-process{Style.RESET_ALL} --help
"""
    
    print(banner)
    print(usage)

def print_status(message, color=Fore.GREEN):
    """Print a colored status message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Fore.BLUE}[{timestamp}]{Style.RESET_ALL} {color}{message}{Style.RESET_ALL}")