from rich.console import Console
from rich.panel import Panel

console = Console()

def print_error(message: str, title: str = "Error") -> None:
    """Prints an error message to the console."""
    console.print(Panel(message, title=title, border_style="red"))

def print_info(message: str, title: str = "Info") -> None:
    """Prints an informational message to the console."""
    console.print(Panel(message, title=title, border_style="yellow"))
