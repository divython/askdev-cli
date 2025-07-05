import re
from typing import Optional, Dict, Any

def parse_stack_trace(log_content: str) -> Optional[Dict[str, Any]]:
    """Parses a stack trace and returns a dictionary with the error details."""
    # This regex handles Java-style stack traces with a message
    java_match = re.search(
        r"Exception in thread \"(.*?)\" (.*?): (.*?)\n\s*at .*?\((.*?):(\d+)\)",
        log_content.strip()
    )
    if java_match:
        return {
            "thread": java_match.group(1),
            "exception": java_match.group(2),
            "message": java_match.group(3),
            "file_path": java_match.group(4),
            "line_number": int(java_match.group(5)),
        }

    # This regex handles Kotlin-style stack traces without a message
    kotlin_match = re.search(
        r"Exception in thread \"(.*?)\" (.*?)\n\s*at .*?\((.*?):(\d+)\)",
        log_content.strip()
    )
    if kotlin_match:
        return {
            "thread": kotlin_match.group(1),
            "exception": kotlin_match.group(2),
            "message": "",
            "file_path": kotlin_match.group(3),
            "line_number": int(kotlin_match.group(4)),
        }

    return None

