# askdev: Android Error CLI Assistant

import typer
import re
import json
from pathlib import Path
from rich import print
from rich.panel import Panel
from typing import Optional

app = typer.Typer()

# Load known errors
ERROR_DB_PATH = Path("error_db.json")
if ERROR_DB_PATH.exists():
    with open(ERROR_DB_PATH) as f:
        ERROR_DB = json.load(f)
else:
    ERROR_DB = {}


def parse_log_file(content: str):
    """
    Advanced log parser: groups stack traces, extracts error types/messages, and context.
    Returns a list of error blocks (dicts).
    """
    errors = []
    current_error = []
    for line in content.splitlines():
        if re.match(r"\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+", line) or line.strip() == '':
            if current_error:
                errors.append('\n'.join(current_error))
                current_error = []
        if 'Exception' in line or 'Error' in line or current_error:
            current_error.append(line)
    if current_error:
        errors.append('\n'.join(current_error))
    return errors if errors else content.splitlines()


def match_known_error(log_block: str):
    for pattern, details in ERROR_DB.items():
        if re.search(pattern, log_block, re.DOTALL):
            return pattern, details
    return None, None


def query_llm(error_text: str, provider: str = "openrouter") -> Optional[str]:
    """
    Placeholder for LLM integration. Replace with actual API call to OpenRouter/Ollama.
    """
    # TODO: Implement real LLM call
    return f"[AI Suggestion Placeholder] This is where an LLM-generated suggestion for: {error_text[:80]}... would appear."


@app.command()
def explain(logfile: Path, ai: bool = typer.Option(False, "--ai", help="Use AI to suggest fixes")):
    """Analyze an Android log file and suggest solutions."""
    if not logfile.exists():
        print("[red]Log file not found.[/red]")
        raise typer.Exit(1)

    content = logfile.read_text(errors="ignore")
    error_blocks = parse_log_file(content)
    found = False
    for block in error_blocks:
        pattern, details = match_known_error(block)
        if pattern:
            print(Panel.fit(
                f"[bold green]🔍 Matched Pattern:[/bold green] {pattern}\n"
                f"[bold cyan]🧠 Cause:[/bold cyan] {details['cause']}\n"
                f"[bold yellow]💡 Suggestion:[/bold yellow] {details['suggestion']}\n"
                f"[bold blue]🔗 Link:[/bold blue] {details.get('link', 'N/A')}"
            ))
            found = True
            break
    if not found:
        if ai:
            ai_suggestion = query_llm('\n'.join(error_blocks))
            print(Panel.fit(f"[bold magenta]🤖 AI Suggestion:[/bold magenta]\n{ai_suggestion}"))
        else:
            print("[bold red]No known error matched. Try again with more logs, use --ai, or update the error database.[/bold red]")


@app.command()
def show_db():
    """Show information about the error database."""
    if ERROR_DB:
        print(f"[green]Database contains {len(ERROR_DB)} error patterns[/green]")
        sample = list(ERROR_DB.keys())[:10]
        print(f"[cyan]Sample error patterns:[/cyan] {sample}")
    else:
        print("[red]No error database loaded.[/red]")


if __name__ == "__main__":
    app()
