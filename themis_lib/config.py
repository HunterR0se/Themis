"""
Configuration settings for Themis
"""
import os
import json
import configparser
from pathlib import Path

# Default model if not provided via command line
DEFAULT_MODEL = "mistral"

# Default to localhost, but can be overridden in config file or command line
DEFAULT_OLLAMA_HOST = "localhost"
DEFAULT_OLLAMA_PORT = 11434

# Build the default API URL
DEFAULT_OLLAMA_API_URL = f"http://{DEFAULT_OLLAMA_HOST}:{DEFAULT_OLLAMA_PORT}/api/generate"

# Configuration file path
CONFIG_FILE = Path.home() / ".themis" / "themis.cfg"

# Default questions file path
DEFAULT_QUESTIONS_FILE = Path(__file__).parent.parent / "questions.md"

# Fallback questions for legal analysis if questions file cannot be loaded
FALLBACK_QUESTIONS = [
    "What are the central claims or charges against the defendant in this document?",
    "What key evidence is presented to support these allegations, including any specific details related to cryptocurrency, digital assets, transactions, or witness statements?",
    "Are there any apparent weaknesses, inconsistencies, or procedural errors in the prosecution's case (such as lack of evidence, jurisdictional issues, or prior conduct references) that could be leveraged in the defense?",
    "What legal precedents, statutes, or regulatory frameworks are referenced, particularly those pertaining to cryptocurrency, digital assets, or asset classification, and how might they impact the case?",
    "What are the imminent deadlines, procedural requirements, or upcoming events (such as status conferences, hearings, detention conditions, or bond matters) that the defense must address promptly?"
]

def get_config():
    """Load configuration from file if it exists, otherwise return defaults"""
    config = {
        "model": DEFAULT_MODEL,
        "ollama_host": DEFAULT_OLLAMA_HOST,
        "ollama_port": DEFAULT_OLLAMA_PORT,
        "ollama_api_url": DEFAULT_OLLAMA_API_URL,
        "questions_file": str(DEFAULT_QUESTIONS_FILE),
        "last_case_dir": ""
    }
    
    if CONFIG_FILE.exists():
        parser = configparser.ConfigParser()
        parser.read(CONFIG_FILE)
        
        if "themis" in parser:
            # Update config with saved values
            if "model" in parser["themis"]:
                config["model"] = parser["themis"]["model"]
            if "ollama_host" in parser["themis"]:
                config["ollama_host"] = parser["themis"]["ollama_host"]
            if "ollama_port" in parser["themis"]:
                config["ollama_port"] = int(parser["themis"]["ollama_port"])
            if "questions_file" in parser["themis"]:
                config["questions_file"] = parser["themis"]["questions_file"]
            if "last_case_dir" in parser["themis"]:
                config["last_case_dir"] = parser["themis"]["last_case_dir"]
                
            # Rebuild the API URL
            config["ollama_api_url"] = f"http://{config['ollama_host']}:{config['ollama_port']}/api/generate"
    
    return config

def save_config(config):
    """Save configuration to file"""
    # Make sure directory exists
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    parser = configparser.ConfigParser()
    parser["themis"] = {
        "model": config.get("model", DEFAULT_MODEL),
        "ollama_host": config.get("ollama_host", DEFAULT_OLLAMA_HOST),
        "ollama_port": str(config.get("ollama_port", DEFAULT_OLLAMA_PORT)),
        "questions_file": config.get("questions_file", str(DEFAULT_QUESTIONS_FILE)),
        "last_case_dir": config.get("last_case_dir", "")
    }
    
    with open(CONFIG_FILE, 'w') as f:
        parser.write(f)
    
    return True

# Initialize OLLAMA_API_URL from config
config = get_config()
OLLAMA_API_URL = config["ollama_api_url"]