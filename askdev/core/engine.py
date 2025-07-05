import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from askdev.core.parser import parse_stack_trace

class ErrorDatabase:
    """Manages the error database."""

    def __init__(self, db_paths: Optional[List[Path]] = None) -> None:
        if db_paths is None:
            self.db_paths = [
                Path("error_db.json"),
                Path.home() / ".askdev" / "error_db.json",
                Path(__file__).parent.parent / "error_db.json",
            ]
        else:
            self.db_paths = db_paths
        self.db = self._load_db()

    def _load_db(self) -> Dict[str, str]:
        """Loads the error database from the first available path."""
        for db_path in self.db_paths:
            if db_path.exists():
                try:
                    with open(db_path) as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    continue
        return self._create_default_db()

    def _create_default_db(self) -> Dict[str, str]:
        """Creates a default error database."""
        return {
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

    def get_error_message(self, error_code: str) -> Optional[str]:
        """Returns the error message for a given error code."""
        return self.db.get(error_code.upper())

class LogAnalyzer:
    """Analyzes log files to find errors and suggest fixes."""

    def __init__(self, db: ErrorDatabase):
        self.db = db

    def analyze_log(self, log_content: str) -> Optional[Tuple[str, str]]:
        """Analyzes a log file and returns the error code and message."""
        parsed_error = parse_stack_trace(log_content)
        if parsed_error:
            # In a real implementation, we would use the parsed error to find a more
            # specific solution in the database.
            error_code = parsed_error["exception"]
            message = self.db.get_error_message(error_code)
            if message:
                return error_code, message

        # Fallback to simple search
        for error_code, message in self.db.db.items():
            if re.search(error_code, log_content, re.IGNORECASE):
                return error_code, message
        return None

class AISuggestionEngine:
    """Provides AI-powered suggestions for fixing errors."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def get_suggestion(self, error_message: str) -> str:
        """Returns an AI-powered suggestion for fixing the error."""
        if not self.api_key:
            return "AI suggestions are disabled. Please provide an API key."
        # In a real implementation, this would make a request to an AI service.
        return f"AI suggestion for: {error_message}"
