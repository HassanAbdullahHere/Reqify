from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

def save_requirements(content: str, filename: str = "requirements.txt"):
    with open(filename, "w") as f:
        f.write(content)
    return f"Requirements saved to {filename}"

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
- (list questions you would ask the client)

When saving requirements, use the project or business name as the filename in lowercase with underscores, e.g. cake_shop_requirements.txt
After extracting requirements, always save them using the save_requirements tool.
When user provides new information, update the requirements and save again.
"""

# Memory — this is the entire conversation history
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

    # Add user message to history
    history.append(
        types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
        )
    )

    # Send full history every time
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[save_tool]
        ),
        contents=history
    )

    assistant_parts = []
    tool_was_called = False

    # First pass — execute tools only
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

    # Second pass — print text only if no tool was called
    if not tool_was_called:
        for part in response.candidates[0].content.parts:
            if part.text:
                print(f"\nReqify: {part.text}")

    # Add assistant response to history
    history.append(
        types.Content(
            role="model",
            parts=assistant_parts
        )
    )