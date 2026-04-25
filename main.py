from google import genai
from google.genai import types
from dotenv import load_dotenv
import json
import os
import threading
import time
import sys
import itertools

load_dotenv()
client = genai.Client()

SUMMARY_FILE = "summary.json"
exchange_count = 0

def save_requirements(content: str, filename: str = "requirements.txt"):
    with open(filename, "w") as f:
        f.write(content)
    return f"Requirements saved to {filename}"

def save_summary(summary: str):
    with open(SUMMARY_FILE, "w") as f:
        json.dump({"summary": summary}, f, indent=2)

def load_summary() -> str:
    if os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, "r") as f:
            return json.load(f)["summary"]
    return None

def summarize_history(history: list) -> str:
    history_text = ""
    for msg in history:
        role = msg.role
        for part in msg.parts:
            if hasattr(part, "text") and part.text:
                history_text += f"{role}: {part.text}\n"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""Summarize this requirements conversation into a compact state snapshot including:
- Project name
- Confirmed features so far
- Unresolved questions
- Last thing discussed
Keep it under 150 words.

Conversation:
{history_text}"""
    )
    return response.text

def build_history_from_summary(summary: str) -> list:
    return [
        types.Content(
            role="user",
            parts=[types.Part(text=f"Context from previous exchanges:\n{summary}")]
        ),
        types.Content(
            role="model",
            parts=[types.Part(text="Understood, continuing from that context.")]
        )
    ]

LOADING_FRAMES = [
    "🧠 Consulting the void...",
    "⚡ Zapping neurons...",
    "🌀 Untangling requirements...",
    "🔮 Reading the crystal spec...",
    "🚀 Launching brain cells...",
    "🎲 Rolling the dice of logic...",
    "🤯 Having a mild epiphany...",
    "🧬 Mutating your brief...",
    "💡 Stealing ideas from the ether...",
    "🐙 Eight arms working at once...",
]

def loading_spinner(stop_event):
    spinner = itertools.cycle(["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"])
    frame_iter = itertools.cycle(LOADING_FRAMES)
    current_msg = next(frame_iter)
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{next(spinner)} {current_msg}  ")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
        if i % 15 == 0:
            current_msg = next(frame_iter)
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()

save_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="save_requirements",
            description="Saves the extracted requirements to a text file",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "content": types.Schema(
                        type="STRING",
                        description="The formatted requirements to save"
                    ),
                    "filename": types.Schema(
                        type="STRING",
                        description="Name of the file to save to"
                    )
                },
                required=["content"]
            )
        )
    ]
)

SYSTEM_PROMPT = """
You are a requirements analyst. When given a client brief, extract and return requirements in this exact structure:

PROJECT SUMMARY:
(one sentence)

CORE FEATURES:
- (list each feature clearly)

UNCLEAR POINTS:
- (list anything ambiguous or missing)

CLARIFYING QUESTIONS:
- (list questions you would ask the client -max 3- to clarify the unclear points)

When saving requirements, use the project or business name as the filename in lowercase with underscores, e.g. cake_shop_requirements.txt
After extracting requirements, always save them using the save_requirements tool.
When user provides new information, update the requirements and save again.
"""

# Load summary from previous session if exists
existing_summary = load_summary()
if existing_summary:
    history = build_history_from_summary(existing_summary)
    print("\n Welcome to Reqify")
    print("Resuming from previous session.\n")
else:
    history = []
    print("\n Welcome to Reqify")
    print("Type your client brief to start. Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "exit":
        print("Goodbye.")
        break

    if not user_input:
        continue

    history.append(
        types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
        )
    )

    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=loading_spinner, args=(stop_event,), daemon=True)
    spinner_thread.start()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[save_tool]
        ),
        contents=history
    )

    stop_event.set()
    spinner_thread.join()

    assistant_parts = []
    tool_was_called = False

    for part in response.candidates[0].content.parts:
        if part.function_call:
            tool_name = part.function_call.name
            tool_args = dict(part.function_call.args)
            if tool_name == "save_requirements":
                result = save_requirements(**tool_args)
                print(f"\n✓ {result}")
                print("\n--- REQIFY OUTPUT ---\n")
                print(tool_args["content"])
                tool_was_called = True
        assistant_parts.append(part)

    if not tool_was_called:
        for part in response.candidates[0].content.parts:
            if part.text:
                print(f"\nReqify: {part.text}")

    history.append(
        types.Content(
            role="model",
            parts=assistant_parts
        )
    )

    # Rolling summary every 2 exchanges
    exchange_count += 1
    if exchange_count % 2 == 0:
        print("\n[Summarizing session...]\n")
        summary = summarize_history(history)
        save_summary(summary)
        history = build_history_from_summary(summary)
        exchange_count = 0