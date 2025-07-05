# askdev: Android Error CLI Assistant

## Overview
askdev is a command-line tool for Android developers to quickly diagnose, explain, and auto-fix common Android errors using a curated error database and AI-powered suggestions. It works with Java, Kotlin, and Flutter/Dart projects, and is IDE-agnostic (works with Android Studio, VS Code, etc.).

## Features
- Pinpoints error locations from logs/stacktraces
- Explains errors and suggests fixes (from database or AI)
- Can auto-fix code (with preview and user confirmation)
- Supports multiple LLM providers (Cohere, Gemini, Hugging Face, OpenRouter, Together, Groq)
- Easy .env-based API key management

## Quickstart (Android Studio or any terminal)

```sh
git clone https://github.com/divython/askdev-cli
cd askdev-cli/app
pip install .
cp .env.example .env
```
- Edit `.env` and add your `ASKDEV_API_KEY` if you want to use AI-powered suggestions.

## Usage

### Analyze and Fix Errors

To analyze and fix errors from a log file:
```sh
askdev fix error.log --project-root .
```

To get AI-powered suggestions (requires `ASKDEV_API_KEY` in your `.env` file):
```sh
askdev fix error.log --ai
```

### Look Up Error Codes

To look up a specific error code from the local database:
```sh
askdev lookup 404
```

To see all commands:
```sh
askdev --help
```

## Android Studio Integration
- Open the terminal in Android Studio.
- Run the CLI commands as above in your project directory.
- Optionally, add as an External Tool in Android Studio for one-click access.

## Security
- **Never commit your real API keys to public repositories!**
- Use the provided `.env.example` for guidance.

## License
MIT License. See [LICENSE](LICENSE).
