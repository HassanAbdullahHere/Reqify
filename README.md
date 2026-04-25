# Reqify

A CLI tool that turns client briefs into structured software requirements using Google Gemini.

## What it does

You paste in a client brief (or describe a project idea), and Reqify extracts:

- **Project Summary** — one-sentence overview
- **Core Features** — clear, actionable feature list
- **Unclear Points** — ambiguities it detected
- **Clarifying Questions** — up to 3 follow-up questions for the client

Requirements are automatically saved to a `.txt` file named after the project. Follow-up messages update the requirements in place.

## Setup

**Prerequisites:** Python 3.11+, [uv](https://github.com/astral-sh/uv)

```bash
git clone https://github.com/HassanAbdullahHere/Reqify
cd Reqify
uv sync
```

Create a `.env` file with your Gemini API key:

```
GEMINI_API_KEY=your_key_here
```

## Usage

```bash
uv run main.py
```

Or on Windows:

```bash
run.bat
```

Type your client brief at the prompt. Type `exit` to quit.

```
Welcome to Reqify
Type your client brief to start. Type 'exit' to quit.

You: I need an app for a toy shop to manage inventory and online orders...

🌀 Untangling requirements...

✓ Requirements saved to toy_shop_requirements.txt

--- REQIFY OUTPUT ---
...
```

## Features

- **Session memory** — conversation is summarized every 2 exchanges and persisted to `summary.json`, so you can resume where you left off
- **Auto-save** — requirements are written to a `.txt` file automatically after each response
- **Iterative refinement** — provide more info and Reqify updates the requirements file

## Stack

- [Google Gemini 2.5 Flash](https://deepmind.google/technologies/gemini/) via `google-genai`
- `python-dotenv` for config
- `uv` for dependency management

## License

[LICENSE](LICENSE)
