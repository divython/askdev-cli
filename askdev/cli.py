# askdev: Android Error CLI Assistant

import dotenv
import typer
import re
import json
import os
import requests
import sys
import difflib
from pathlib import Path
from rich import print
from rich.panel import Panel
from typing import Optional

def run_main():
    dotenv.load_dotenv()
    app = typer.Typer()

    # Load known errors - check multiple locations
    ERROR_DB_PATHS = [
        Path("error_db.json"),  # Local directory
        Path.home() / ".askdev" / "error_db.json",  # User config
        Path(__file__).parent / "error_db.json"  # Package directory
    ]

    ERROR_DB = {}
    for db_path in ERROR_DB_PATHS:
        if db_path.exists():
            try:
                with open(db_path) as f:
                    ERROR_DB = json.load(f)
                break
            except json.JSONDecodeError:
                continue

    # If no error database found, create a default one
    if not ERROR_DB:
        ERROR_DB = {
            "404": "Not Found - The requested resource could not be found.",
            "500": "Internal Server Error - The server encountered an unexpected condition.",
            "403": "Forbidden - The server understood the request, but is refusing to fulfill it.",
            "401": "Unauthorized - Authentication is required and has failed or has not yet been provided.",
            "400": "Bad Request - The server could not understand the request due to invalid syntax.",
            "408": "Request Timeout - The server timed out waiting for the request.",
            "429": "Too Many Requests - The user has sent too many requests in a given amount of time.",
            "503": "Service Unavailable - The server is currently unable to handle the request due to temporary overloading or maintenance.",
            "504": "Gateway Timeout - The server, while acting as a gateway or proxy, did not receive a timely response from the upstream server.",
        }

    @app.command()
    def main(
        error_code: Optional[str] = typer.Argument(None, help="The error code to look up."),
        raw: bool = typer.Option(False, "--raw", help="Show raw error message."),
    ):
        """Lookup and display error information."""
        if error_code:
            error_code = error_code.upper()
            if error_code in ERROR_DB:
                message = ERROR_DB[error_code]
                if not raw:
                    message = Panel(message, title=f"Error {error_code}", border_style="red")
                print(message)
            else:
                print(f"[red]Error code {error_code} not found in the database.[/red]")
        else:
            print("[yellow]No error code provided. Please specify an error code.[/yellow]")

    app()
