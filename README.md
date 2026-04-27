# Reqify

A CLI tool that turns client briefs into structured software requirements.
Powered by Google Gemini.

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

## How it works

1. **Input** — you type a client brief at the prompt
2. **History build** — your message is appended to a running conversation history sent to Gemini on every turn, giving the model full context
3. **Generation** — Gemini 2.5 Flash processes the brief against a fixed system prompt that enforces the output structure
4. **Tool call** — the model calls the `save_requirements` tool with the formatted output; Reqify intercepts this, writes the `.txt` file, and prints the result
5. **Rolling summary** — every 2 exchanges the full history is compressed into a ~150-word snapshot via a second Gemini call and saved to `summary.json`; the in-memory history is replaced with this summary to keep token usage low
6. **Resume** — on next launch, if `summary.json` exists, Reqify injects the snapshot as context so the conversation continues where it left off

## Stack

- [Google Gemini 2.5 Flash](https://deepmind.google/technologies/gemini/) via `google-genai`
- `python-dotenv` for config
- `uv` for dependency management

## License

[LICENSE](LICENSE)
