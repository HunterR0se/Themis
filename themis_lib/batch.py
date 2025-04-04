"""
Batch processing module for running Themis with multiple models
"""
import sys
import time
import requests
import json
from pathlib import Path
from datetime import datetime
from colorama import Fore

from themis_lib.ui import print_status
from themis_lib.utils import sanitize_model_name
from themis_lib.config import OLLAMA_API_URL

def get_available_models(api_url=None):
    """Get a list of all available models from the Ollama server"""
    if api_url is None:
        api_url = OLLAMA_API_URL
    
    try:
        url = api_url.replace('/api/generate', '/api/tags')
        print_status(f"Querying Ollama for available models...", Fore.YELLOW)
        response = requests.get(url)
        
        if response.status_code == 200:
            models = [m['name'] for m in response.json().get('models', [])]
            print_status(f"Found {len(models)} models on Ollama server", Fore.GREEN)
            return models
        else:
            print_status(f"Failed to get models: {response.text}", Fore.RED)
            return []
    except Exception as e:
        print_status(f"Error connecting to Ollama server: {str(e)}", Fore.RED)
        return []

def generate_comparison_summary(case_dir, successful_models, failed_models):
    """Generate a summary comparing the results of all model runs"""
    if not successful_models:
        print_status("No successful models to compare.", Fore.YELLOW)
        return
    
    print_status("\nGenerating comparison summary...", Fore.MAGENTA)
    summary_path = Path(case_dir) / f"model_comparison_{datetime.now().strftime('%Y%m%d')}.md"
    
    with open(summary_path, 'w') as f:
        f.write(f"# Themis Model Comparison\n\n")
        f.write(f"Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')}\n\n")
        
        f.write(f"## Models Compared\n\n")
        f.write("### Successful Models\n\n")
        for i, model in enumerate(successful_models, 1):
            f.write(f"{i}. {model}\n")
        
        if failed_models:
            f.write("\n### Failed Models\n\n")
            for i, model in enumerate(failed_models, 1):
                f.write(f"{i}. {model}\n")
        
        f.write("\n## Results\n\n")
        f.write("| Model | Analysis | Defense Strategy | Combined Report |\n")
        f.write("|-------|----------|------------------|------------------|\n")
        
        date_str = datetime.now().strftime('%Y%m%d')
        for model in successful_models:
            # Use sanitized model name for filenames
            sanitized = sanitize_model_name(model)
            
            analysis_path = Path(case_dir) / f"{date_str}_{sanitized}" / f"document_analysis_{sanitized}.md"
            defense_path = Path(case_dir) / f"{date_str}_{sanitized}" / "defense_materials" / "defense_strategy.md"
            combined_path = Path(case_dir) / f"{date_str}_{sanitized}.md"
            
            analysis_rel = f"{date_str}_{sanitized}/document_analysis_{sanitized}.md"
            defense_rel = f"{date_str}_{sanitized}/defense_materials/defense_strategy.md"
            combined_rel = f"{date_str}_{sanitized}.md"
            
            analysis_link = f"[Analysis]({analysis_rel})" if analysis_path.exists() else "❌"
            defense_link = f"[Strategy]({defense_rel})" if defense_path.exists() else "❌"
            combined_link = f"[Report]({combined_rel})" if combined_path.exists() else "❌"
            
            f.write(f"| {model} | {analysis_link} | {defense_link} | {combined_link} |\n")
    
    print_status(f"Comparison summary saved to {summary_path}", Fore.GREEN)
    return summary_path