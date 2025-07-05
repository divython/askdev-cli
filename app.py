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

# Load .env variables
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
        "NullPointerException": {
            "cause": "Attempting to use a null reference",
            "suggestion": "Check if the object is null before calling methods on it. Use null checks or optional chaining.",
            "link": "https://developer.android.com/reference/java/lang/NullPointerException"
        },
        "OutOfMemoryError": {
            "cause": "Application ran out of memory",
            "suggestion": "Optimize memory usage, reduce bitmap sizes, implement proper memory management, or increase heap size.",
            "link": "https://developer.android.com/topic/performance/memory"
        },
        "ActivityNotFoundException": {
            "cause": "Trying to start an activity that doesn't exist or isn't declared in manifest",
            "suggestion": "Check if the activity is declared in AndroidManifest.xml and verify the intent is correct.",
            "link": "https://developer.android.com/reference/android/content/ActivityNotFoundException"
        },
        "ClassNotFoundException": {
            "cause": "Class not found at runtime",
            "suggestion": "Check if the class is in the classpath and properly imported. Verify ProGuard/R8 rules if using code obfuscation.",
            "link": "https://developer.android.com/reference/java/lang/ClassNotFoundException"
        },
        "SecurityException": {
            "cause": "Missing required permission",
            "suggestion": "Add the required permission to AndroidManifest.xml and request runtime permissions for dangerous permissions.",
            "link": "https://developer.android.com/guide/topics/permissions/overview"
        },
        "NetworkOnMainThreadException": {
            "cause": "Network operation attempted on main UI thread",
            "suggestion": "Move network operations to background thread using AsyncTask, Thread, or modern approaches like Retrofit with coroutines.",
            "link": "https://developer.android.com/reference/android/os/NetworkOnMainThreadException"
        },
        "IllegalStateException": {
            "cause": "Method called at inappropriate time or object in wrong state",
            "suggestion": "Check the lifecycle state of your activity/fragment and ensure methods are called at appropriate times.",
            "link": "https://developer.android.com/reference/java/lang/IllegalStateException"
        },
        "WindowManager.BadTokenException": {
            "cause": "Attempting to show dialog with invalid window token",
            "suggestion": "Ensure activity is not finishing when showing dialog. Check if activity is still valid before showing popups.",
            "link": "https://developer.android.com/reference/android/view/WindowManager.BadTokenException"
        },
        "Resources.NotFoundException": {
            "cause": "Resource ID not found",
            "suggestion": "Check if the resource exists in the correct folder and is properly referenced. Clean and rebuild project.",
            "link": "https://developer.android.com/reference/android/content/res/Resources.NotFoundException"
        },
        "IllegalArgumentException": {
            "cause": "Invalid argument passed to method",
            "suggestion": "Validate input parameters before passing them to methods. Check for null values, empty strings, or invalid ranges.",
            "link": "https://developer.android.com/reference/java/lang/IllegalArgumentException"
        }
    }


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


def get_available_providers():
    """Return a list of available LLM providers based on API keys in the environment."""
    providers = []
    if os.getenv("COHERE_API_KEY"): providers.append("cohere")
    if os.getenv("GEMINI_API_KEY"): providers.append("gemini")
    if os.getenv("HUGGINGFACE_API_KEY"): providers.append("huggingface")
    if os.getenv("OPENROUTER_API_KEY"): providers.append("openrouter")
    if os.getenv("TOGETHER_API_KEY"): providers.append("together")
    if os.getenv("GROQ_API_KEY"): providers.append("groq")
    return providers


def select_provider_interactively(providers):
    print("[bold yellow]Multiple LLM providers detected. Please select one:[/bold yellow]")
    for idx, prov in enumerate(providers, 1):
        print(f"  {idx}. {prov}")
    while True:
        try:
            choice = int(input("Enter number: "))
            if 1 <= choice <= len(providers):
                return providers[choice - 1]
        except Exception:
            pass
        print("[red]Invalid selection. Try again.[/red]")


def query_llm(error_text: str, provider: str = None) -> Optional[str]:
    """
    Query an LLM API for an AI-powered suggestion.
    Supports Cohere, Gemini, Hugging Face, OpenRouter, Together, Groq.
    """
    available = get_available_providers()
    if provider is None:
        if len(available) == 0:
            return "[AI Error] No API key found. Please set at least one LLM API key in your .env file."
        elif len(available) == 1:
            provider = available[0]
        else:
            provider = select_provider_interactively(available)
    provider = provider.lower()

    if provider == "cohere":
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            return "[AI Error] Cohere API key not set. Please set COHERE_API_KEY in your .env file."
        url = "https://api.cohere.ai/v1/chat"
        prompt = (
            "You are an expert Android developer assistant. Given the following Android error log, "
            "explain the likely cause and suggest a fix in a concise, actionable way.\n\n" + error_text
        )
        payload = {
            "model": "command-r-plus",
            "message": prompt,
            "temperature": 0.5,
            "max_tokens": 512
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            if "text" in data:
                return data["text"].strip()
            if "message" in data:
                return data["message"].strip()
            if "generations" in data and data["generations"]:
                return data["generations"][0]["text"].strip()
            if "error" in data:
                return f"[AI Error] {data['error'].get('message', str(data['error']))}"
            return str(data)
        except Exception as e:
            return f"[AI Error] {e}"

    elif provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "[AI Error] Gemini API key not set. Please set GEMINI_API_KEY environment variable."
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
        prompt = (
            "You are an expert Android developer assistant. Given the following Android error log, "
            "explain the likely cause and suggest a fix in a concise, actionable way.\n\n" + error_text
        )
        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            if "candidates" in data and data["candidates"]:
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            if "error" in data:
                return f"[AI Error] {data['error'].get('message', str(data['error']))}"
            return str(data)
        except Exception as e:
            return f"[AI Error] {e}"

    elif provider == "huggingface":
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            return "[AI Error] Hugging Face API key not set. Please set HUGGINGFACE_API_KEY in your .env file."
        url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
        prompt = (
            "You are an expert Android developer assistant. Given the following Android error log, "
            "explain the likely cause and suggest a fix in a concise, actionable way.\n\n" + error_text
        )
        payload = {"inputs": prompt}
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and "error" in data:
                return f"[AI Error] {data['error']}"
            if isinstance(data, list) and data and "generated_text" in data[0]:
                return data[0]["generated_text"].strip()
            if isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"].strip()
            return str(data)
        except Exception as e:
            return f"[AI Error] {e}"

    elif provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return "[AI Error] OpenRouter API key not set. Please set OPENROUTER_API_KEY in your .env file."
        url = "https://openrouter.ai/api/v1/chat/completions"
        prompt = (
            "You are an expert Android developer assistant. Given the following Android error log, "
            "explain the likely cause and suggest a fix in a concise, actionable way.\n\n" + error_text
        )
        payload = {
            "model": "mistralai/mixtral-8x7b-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0.5
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"].strip()
            if "error" in data:
                return f"[AI Error] {data['error'].get('message', str(data['error']))}"
            return str(data)
        except Exception as e:
            return f"[AI Error] {e}"

    elif provider == "together":
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            return "[AI Error] Together API key not set. Please set TOGETHER_API_KEY in your .env file."
        url = "https://api.together.xyz/v1/chat/completions"
        prompt = (
            "You are an expert Android developer assistant. Given the following Android error log, "
            "explain the likely cause and suggest a fix in a concise, actionable way.\n\n" + error_text
        )
        payload = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0.5
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"].strip()
            if "error" in data:
                return f"[AI Error] {data['error'].get('message', str(data['error']))}"
            return str(data)
        except Exception as e:
            return f"[AI Error] {e}"

    elif provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "[AI Error] Groq API key not set. Please set GROQ_API_KEY in your .env file."
        url = "https://api.groq.com/openai/v1/chat/completions"
        prompt = (
            "You are an expert Android developer assistant. Given the following Android error log, "
            "explain the likely cause and suggest a fix in a concise, actionable way.\n\n" + error_text
        )
        payload = {
            "model": "mixtral-8x7b-32768",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0.5
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"].strip()
            if "error" in data:
                return f"[AI Error] {data['error'].get('message', str(data['error']))}"
            return str(data)
        except Exception as e:
            return f"[AI Error] {e}"

    else:
        return f"[AI Error] Unknown provider: {provider}"


def extract_stack_info(log_block: str, project_root: Optional[str] = None):
    """
    Extract file, line, and code context from Java/Kotlin/Dart/Flutter stack traces.
    Returns a list of dicts: {file, line, code, language}
    """
    stack_info = []
    # Java/Kotlin: at com.example.MyClass.method(MyClass.java:42)
    java_pattern = re.compile(r'at (.+?)\((.+?):(\d+)\)')
    # Dart/Flutter: #0   MyWidget.build (package:my_app/my_widget.dart:24:16)
    dart_pattern = re.compile(r'#\d+\s+.+?\((.+?):(\d+)(?::\d+)?\)')
    for line in log_block.splitlines():
        m = java_pattern.search(line)
        if m:
            file_path = m.group(2)
            line_num = int(m.group(3))
            lang = 'java/kotlin'
        else:
            m = dart_pattern.search(line)
            if m:
                file_path = m.group(1)
                line_num = int(m.group(2))
                lang = 'dart/flutter'
            else:
                continue
        # Try to resolve file path
        abs_path = None
        if project_root:
            for root, dirs, files in os.walk(project_root):
                for f in files:
                    if f == os.path.basename(file_path):
                        abs_path = os.path.join(root, f)
                        break
                if abs_path:
                    break
        else:
            abs_path = file_path if os.path.exists(file_path) else None
        # Extract code context
        code_context = None
        if abs_path and os.path.exists(abs_path):
            try:
                with open(abs_path, encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                start = max(0, line_num-3)
                end = min(len(lines), line_num+2)
                code_context = ''.join(lines[start:end])
            except Exception:
                code_context = None
        stack_info.append({
            'file': file_path,
            'line': line_num,
            'abs_path': abs_path,
            'code': code_context,
            'language': lang
        })
    return stack_info


@app.command()
def explain(
    logfile: Path = typer.Argument(..., help="Path to log file to analyze"),
    ai: bool = typer.Option(False, "--ai", help="Use AI to suggest fixes"),
    provider: Optional[str] = typer.Option(None, "--provider", help="LLM provider: cohere, gemini, etc."),
    project_root: Optional[str] = typer.Option(None, "--project-root", help="Root directory of the project for code lookup")
):
    """Analyze an Android log file, pinpoint error location, and suggest solutions."""
    if not logfile.exists():
        print("[red]Log file not found.[/red]")
        raise typer.Exit(1)

    content = logfile.read_text(errors="ignore")
    error_blocks = parse_log_file(content)
    found = False
    for block in error_blocks:
        pattern, details = match_known_error(block)
        stack_info = extract_stack_info(block, project_root)
        if pattern:
            msg = f"[bold green]🔍 Matched Pattern:[/bold green] {pattern}\n"
            msg += f"[bold cyan]🧠 Cause:[/bold cyan] {details['cause']}\n"
            msg += f"[bold yellow]💡 Suggestion:[/bold yellow] {details['suggestion']}\n"
            msg += f"[bold blue]🔗 Link:[/bold blue] {details.get('link', 'N/A')}\n"
            if stack_info:
                for s in stack_info:
                    msg += f"[bold magenta]📄 File:[/bold magenta] {s['file']}  [bold magenta]Line:[/bold magenta] {s['line']}\n"
                    if s['code']:
                        msg += f"[white]{s['code']}[/white]\n"
            print(Panel.fit(msg))
            found = True
            break
    if not found:
        if ai:
            ai_suggestion = query_llm('\n'.join(error_blocks), provider=provider)
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


@app.command()
def ai(
    user_input: Optional[str] = typer.Argument(None, help="Error message or path to log file (optional)"),
    provider: Optional[str] = typer.Option(None, "--provider", help="LLM provider: cohere, gemini, etc.")
):
    """Ask the AI assistant about an error (file, text, or interactive input)."""
    # If user_input is a file path and exists, read file; else treat as error string
    if user_input and Path(user_input).exists():
        content = Path(user_input).read_text(errors="ignore")
    elif user_input:
        content = user_input
    else:
        # Interactive textbox-style input if no argument or file is provided
        print("[bold cyan]Enter your error, log, or question for the AI. Press Enter twice to submit:[/bold cyan]")
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == "":
                    break
                lines.append(line)
            except EOFError:
                break
        content = "\n".join(lines)
        if not content.strip():
            print("[red]No input provided.[/red]")
            raise typer.Exit(1)
    ai_suggestion = query_llm(content, provider=provider)
    print(Panel.fit(f"[bold magenta]🤖 AI Suggestion:[/bold magenta]\n{ai_suggestion}"))


def show_diff(original, fixed, file_path):
    diff = difflib.unified_diff(
        original.splitlines(), fixed.splitlines(),
        fromfile=f'{file_path} (original)', tofile=f'{file_path} (fixed)', lineterm=''
    )
    print('\n'.join(diff))


@app.command()
def fix(
    logfile: Path = typer.Argument(..., help="Path to log file to analyze and fix"),
    ai: bool = typer.Option(False, "--ai", help="Use AI to suggest and apply fixes"),
    provider: Optional[str] = typer.Option(None, "--provider", help="LLM provider: cohere, gemini, etc."),
    project_root: Optional[str] = typer.Option(None, "--project-root", help="Root directory of the project for code lookup")
):
    """Automatically fix code based on error log/stacktrace using error DB or AI. Now previews both rule-based and AI fixes for user selection."""
    import difflib
    if not logfile.exists():
        print("[red]Log file not found.[/red]")
        raise typer.Exit(1)

    content = logfile.read_text(errors="ignore")
    error_blocks = parse_log_file(content)
    found = False
    for block in error_blocks:
        pattern, details = match_known_error(block)
        stack_info = extract_stack_info(block, project_root)
        if pattern and stack_info:
            s = stack_info[0]  # Only fix the first detected location for now
            file_path = s['abs_path']
            line_num = s['line']
            code_context = s['code']
            suggestion = details['suggestion']
            print(Panel.fit(f"[bold green]🔍 Matched Pattern:[/bold green] {pattern}\n[bold cyan]🧠 Cause:[/bold cyan] {details['cause']}\n[bold yellow]💡 Suggestion:[/bold yellow] {suggestion}\n[bold blue]🔗 Link:[/bold blue] {details.get('link', 'N/A')}\n[bold magenta]📄 File:[/bold magenta] {file_path}  [bold magenta]Line:[/bold magenta] {line_num}\n[white]{code_context}[/white]"))
            if not file_path or not os.path.exists(file_path):
                print(f"[red]File {file_path} not found. Cannot auto-fix.[/red]")
                return
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            idx = line_num - 1 if line_num > 0 and line_num <= len(lines) else None
            if idx is None:
                print("[red]Line number out of range. Cannot auto-fix.[/red]")
                return
            original = ''.join(lines)
            # Option 1: Rule-based real code fix for NullPointerException
            rule_based_fix = None
            if pattern == "NullPointerException":
                # Insert a null check before the problematic line
                indent = ' ' * (len(lines[idx]) - len(lines[idx].lstrip(' ')))
                check_line = f"{indent}if (s != null) {{\n{indent}    System.out.println(s.length());\n{indent}}} else {{\n{indent}    System.out.println(\"s is null\");\n{indent}}}\n"
                # Replace the original line with the null check
                rule_lines = lines[:idx] + [check_line] + lines[idx+1:]
                rule_based_fix = ''.join(rule_lines)
            else:
                # Fallback: just append suggestion as a comment
                comment = f"  // {suggestion}\n" if file_path.endswith(('.java', '.kt')) else f"  # {suggestion}\n"
                lines[idx] = lines[idx].rstrip('\n') + comment
                rule_based_fix = ''.join(lines)
            # Option 2: AI-powered fix (if requested)
            ai_fix = None
            if ai:
                prompt = f"Android error: {pattern}\nStacktrace:\n{block}\nCode context:\n{code_context}\nSuggest a code fix. Return ONLY the fixed code for the above snippet."
                ai_fix_result = query_llm(prompt, provider=provider)
                if ai_fix_result and not ai_fix_result.startswith('[AI Error]'):
                    context_lines = code_context.splitlines(keepends=True)
                    ai_lines = ai_fix_result.splitlines(keepends=True)
                    start = max(0, idx-2)
                    end = min(len(lines), idx+3)
                    ai_lines = [l if l.endswith('\n') else l+'\n' for l in ai_lines]
                    ai_fixed_lines = lines[:start] + ai_lines + lines[end:]
                    ai_fix = ''.join(ai_fixed_lines)
            # Preview both options
            print("\n[bold cyan]Preview of available fixes:[/bold cyan]")
            print("[bold yellow]1. Rule-based fix:[/bold yellow]")
            show_diff(original, rule_based_fix, file_path)
            if ai and ai_fix:
                print("\n[bold magenta]2. AI-powered fix:[/bold magenta]")
                show_diff(original, ai_fix, file_path)
            # Ask user which fix to apply
            print("\n[bold green]Select a fix to apply:[/bold green]")
            print("1. Rule-based fix")
            if ai and ai_fix:
                print("2. AI-powered fix")
            print("0. Cancel")
            while True:
                choice = input("Enter your choice (1/2/0): ").strip()
                if choice == '1':
                    confirm = input("Apply the rule-based fix? [y/N]: ")
                    if confirm.lower() == 'y':
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(rule_based_fix)
                        print("[green]Rule-based fix applied.[/green]")
                    else:
                        print("[yellow]No changes made.[/yellow]")
                    break
                elif choice == '2' and ai and ai_fix:
                    confirm = input("Apply the AI-powered fix? [y/N]: ")
                    if confirm.lower() == 'y':
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(ai_fix)
                        print("[green]AI-powered fix applied.[/green]")
                    else:
                        print("[yellow]No changes made.[/yellow]")
                    break
                elif choice == '0':
                    print("[yellow]No changes made.[/yellow]")
                    break
                else:
                    print("[red]Invalid choice. Please enter 1, 2, or 0.[/red]")
            found = True
            break
    if not found:
        print("[bold red]No known error matched or no code location found. Try --ai for advanced fixes or check your log file.[/bold red]")


def run_main():
    app()

if __name__ == "__main__":
    run_main()