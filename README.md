# askdev: Android Error CLI Assistant

## Overview
askdev is a command-line tool for Android developers to quickly diagnose, explain, and auto-fix common Android errors using a curated error database and AI-powered suggestions. It works with Java, Kotlin, and Flutter/Dart projects, and is IDE-agnostic (works with Android Studio, VS Code, etc.).

## Features
- Pinpoints error locations from logs/stacktraces
- Explains errors and suggests fixes (from database or AI)
- Can auto-fix code (with preview and user confirmation)
- Supports multiple LLM providers (Cohere, Gemini, Hugging Face, OpenRouter, Together, Groq)
- Easy .env-based API key management

## Installation
1. Clone this repository:
   ```sh
   git clone <repo-url>
   cd app
   ```
2. Install with pip (from the project root):
   ```sh
   pip install .
   ```
3. Copy `.env` and add your own API keys (optional for AI):
   ```sh
   cp .env .env.local
   # Edit .env.local and add your API keys
   ```

## Usage
- Analyze and fix errors from a log file:
  ```sh
  askdev fix error.log --project-root .
  ```
- Preview both rule-based and AI-powered fixes (if API key provided):
  ```sh
  askdev fix error.log --ai --project-root .
  ```
- See all commands:
  ```sh
  askdev --help
  ```

## Android Studio Integration
- Open the terminal in Android Studio.
- Run the CLI commands as above in your project directory.
- Optionally, add as an External Tool in Android Studio for one-click access.

## Security
- **Never commit your real API keys to public repositories!**
- Only use the provided `.env` template for sharing.

## License
MIT License. See [LICENSE](LICENSE).
