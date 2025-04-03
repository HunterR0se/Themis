"""
DefenseGenerator class for generating defense materials
"""
import json
from pathlib import Path
import time
from datetime import datetime
from colorama import Fore

from themis_lib.ui import print_status
from themis_lib.config import DEFAULT_MODEL
from themis_lib.utils import query_ollama, setup_logging

class DefenseGenerator:
    """Generates defense materials based on document analysis results"""
    
    def __init__(self, case_dir, model=DEFAULT_MODEL, analysis_file=None, api_url=None):
        self.case_dir = Path(case_dir).expanduser()
        self.model = model
        self.api_url = api_url

        # Create a date and model-specific directory in the case directory
        self.output_dir = self.case_dir / f"{datetime.now().strftime('%Y%m%d')}_{self.model}"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print_status(f"Initializing defense generator with model: {Fore.CYAN}{model}{Fore.GREEN}", Fore.GREEN)
        print_status(f"Case directory: {Fore.CYAN}{self.case_dir}{Fore.GREEN}", Fore.GREEN)
        print_status(f"Using output directory: {Fore.CYAN}{self.output_dir}{Fore.GREEN}", Fore.GREEN)

        # If a specific analysis file is provided, use it; otherwise construct from model name
        if analysis_file:
            self.analysis_file = Path(analysis_file).expanduser()
        else:
            self.analysis_file = self.case_dir / f"document_analysis_{model}.json"

        print_status(f"Using analysis file: {Fore.CYAN}{self.analysis_file}{Fore.GREEN}", Fore.GREEN)

        # Set up logging
        self.log_path = self.output_dir / "defense_generation.log"
        self.logger = setup_logging(self.log_path, f'defense_{self.model}')

        # Load analysis data
        self.load_analysis()

    def load_analysis(self):
        """Load the document analysis results"""
        try:
            print_status(f"Loading analysis data from {Fore.CYAN}{self.analysis_file}{Fore.YELLOW}...", Fore.YELLOW)
            with open(self.analysis_file, 'r') as f:
                self.analysis_data = json.load(f)
            doc_count = len(self.analysis_data)
            print_status(f"Successfully loaded analysis for {Fore.CYAN}{doc_count}{Fore.GREEN} documents", Fore.GREEN)

            # Display document names
            for i, doc in enumerate(self.analysis_data, 1):
                print_status(f"  Document {i}: {Fore.CYAN}{doc['filename']}{Fore.GREEN}", Fore.GREEN)

            self.logger.info(f"Successfully loaded analysis from {self.analysis_file}")
        except FileNotFoundError:
            self.logger.error(f"Analysis file not found: {self.analysis_file}")
            print_status(f"Analysis file not found: {self.analysis_file}", Fore.RED)
            print_status(f"Please run analysis with model '{self.model}' first", Fore.RED)
            raise FileNotFoundError(f"Analysis file not found: {self.analysis_file}")
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON in analysis file: {self.analysis_file}")
            print_status(f"Invalid JSON in analysis file: {self.analysis_file}", Fore.RED)
            raise

    def generate_defense_strategy(self):
        """Generate overall defense strategy based on document analysis"""
        print_status(f"Generating defense strategy...", Fore.MAGENTA)

        # Compile relevant information from analysis
        summary = "Document Analysis Summary:\n\n"
        for doc in self.analysis_data:
            summary += f"Document: {doc['filename']}\n"
            for question, answer in doc['analysis'].items():
                summary += f"{question}\n{answer}\n\n"

        prompt = f"""
        Based on the following case document analysis, generate a comprehensive legal defense strategy.
        Please include:
        1. Key defense arguments
        2. Potential weaknesses in the prosecution's case
        3. Recommended counter-arguments
        4. Suggested evidence to gather or present
        5. Possible legal precedents to cite
        6. Strategic recommendations

        Analysis Summary:
        {summary[:6000]}  # Using first 6000 chars to avoid token limits
        """

        strategy = query_ollama(self.model, prompt, "defense strategy", self.logger, self.api_url)
        return strategy

    def generate_action_items(self):
        """Generate specific action items for the defense"""
        print_status(f"Generating action items...", Fore.MAGENTA)

        prompt = """
        Based on the defense strategy, please generate a list of specific action items that need to be completed.
        Include:
        1. Evidence collection tasks
        2. Witness interviews needed
        3. Legal research requirements
        4. Motion filing deadlines
        5. Expert consultation needs
        Format as a detailed checklist with priorities and responsible parties.
        """

        action_items = query_ollama(self.model, prompt, "action items", self.logger, self.api_url)
        return action_items

    def generate_timeline(self):
        """Generate a timeline of events from the case documents"""
        print_status(f"Generating case timeline...", Fore.MAGENTA)

        timeline_prompt = """
        Based on the document analysis, create a chronological timeline of events relevant to the case.
        Include:
        1. Key dates and events
        2. Filing deadlines
        3. Important procedural dates
        4. Relevant historical events
        Format as a clear chronological sequence from earliest to latest date, with importance flags.
        """

        timeline = query_ollama(self.model, timeline_prompt, "timeline", self.logger, self.api_url)
        return timeline

    def generate_all_materials(self):
        """Generate all defense materials and save them to the output directory"""
        # Create output directory with model name in the logs directory
        defense_output_dir = self.output_dir / "defense_materials"
        defense_output_dir.mkdir(exist_ok=True)

        # Create a corresponding directory in the case directory for easy reference
        case_defense_dir = Path(f"{self.case_dir}/Defense-{datetime.now().strftime('%Y%m%d')}-{self.model}").expanduser()
        case_defense_dir.mkdir(exist_ok=True)

        print_status("Beginning defense material generation...", Fore.MAGENTA)
        start_time = time.time()

        # Generate the materials
        defense_strategy = self.generate_defense_strategy()
        action_items = self.generate_action_items()
        timeline = self.generate_timeline()

        # Save results to both directories
        print_status(f"Saving results to output directories...", Fore.GREEN)

        # Function to write to both locations
        def write_to_both(filename, content):
            # Write to logs directory
            with open(defense_output_dir / filename, 'w') as f:
                f.write(content)
            # Write to case directory
            with open(case_defense_dir / filename, 'w') as f:
                f.write(content)

        # Write defense materials
        write_to_both("defense_strategy.md", "# Defense Strategy\n\n" + defense_strategy)
        write_to_both("action_items.md", "# Action Items\n\n" + action_items)
        write_to_both("case_timeline.md", "# Case Timeline\n\n" + timeline)

        # Calculate total time
        total_time = time.time() - start_time
        minutes, seconds = divmod(total_time, 60)
        time_str = f"{int(minutes)}m {int(seconds)}s"

        print_status(f"Defense generation complete in {time_str}!", Fore.GREEN)
        print_status(f"Generated 3 documents:", Fore.GREEN)
        print_status(f"  - {Fore.CYAN}defense_strategy.md{Fore.GREEN} ({len(defense_strategy)} chars)", Fore.GREEN)
        print_status(f"  - {Fore.CYAN}action_items.md{Fore.GREEN} ({len(action_items)} chars)", Fore.GREEN)
        print_status(f"  - {Fore.CYAN}case_timeline.md{Fore.GREEN} ({len(timeline)} chars)", Fore.GREEN)
        print_status(f"Materials saved to:", Fore.GREEN)
        print_status(f"  - {Fore.CYAN}{defense_output_dir}{Fore.GREEN} (log directory)", Fore.GREEN)
        print_status(f"  - {Fore.CYAN}{case_defense_dir}{Fore.GREEN} (case directory)", Fore.GREEN)

        self.logger.info(f"Defense materials generated and saved to {defense_output_dir} and {case_defense_dir}")
        
        # Return paths for reference
        return {
            "defense_strategy": str(case_defense_dir / "defense_strategy.md"),
            "action_items": str(case_defense_dir / "action_items.md"),
            "case_timeline": str(case_defense_dir / "case_timeline.md"),
        }