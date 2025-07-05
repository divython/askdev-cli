import typer
from typing import Optional
from pathlib import Path
import dotenv
import os

from askdev.core.engine import ErrorDatabase, LogAnalyzer, AISuggestionEngine
from askdev.tui.prompts import print_error, print_info

def run_main():
    # Load .env file
    dotenv.load_dotenv()
    app = typer.Typer()
    db = ErrorDatabase()
    log_analyzer = LogAnalyzer(db)

    @app.command()
    def lookup(
        error_code: Optional[str] = typer.Argument(None, help="The error code to look up."),
        raw: bool = typer.Option(False, "--raw", help="Show raw error message."),
    ):
        """Lookup and display error information from the local database."""
        if error_code:
            message = db.get_error_message(error_code)
            if message:
                if not raw:
                    print_info(message, title=f"Error {error_code}")
                else:
                    print(message)
            else:
                print_error(f"Error code {error_code} not found in the database.")
        else:
            print_info("No error code provided. Please specify an error code.")

    @app.command()
    def fix(
        log_file: Path = typer.Argument(..., help="Path to the error log file.", exists=True, readable=True, file_okay=True),
        project_root: Path = typer.Option(".", "--project-root", help="Path to the project root directory.", exists=True, file_okay=False, dir_okay=True),
        ai: bool = typer.Option(False, "--ai", help="Use AI-powered suggestions (requires API key)."),
    ):
        """Analyze an error log, explain it, and suggest a fix."""
        print_info(f"Analyzing log file: {log_file}")
        log_content = log_file.read_text()
        analysis_result = log_analyzer.analyze_log(log_content)

        if analysis_result:
            error_code, message = analysis_result
            print_info(message, title=f"Detected Error: {error_code}")

            if ai:
                api_key = os.getenv("ASKDEV_API_KEY")
                ai_engine = AISuggestionEngine(api_key)
                suggestion = ai_engine.get_suggestion(message)
                print_info(suggestion, title="AI Suggestion")
        else:
            print_error("Could not identify a known error in the log file.")

    app()
