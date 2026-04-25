from google import genai
from google.genai import types
from dotenv import load_dotenv
import json

load_dotenv()
client = genai.Client()

# Tool function
def save_requirements(content: str, filename: str = "requirements.txt"):
    """Saves extracted requirements to a file"""
    with open(filename, "w") as f:
        f.write(content)
    return f"Requirements saved to {filename}"

# Tool definition
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

After extracting requirements, always save them to a file using the save_requirements tool.
"""

brief = input("Paste your client brief: ")

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[save_tool]
    ),
    contents=brief
)

# Handle tool use loop
for part in response.candidates[0].content.parts:
    if part.function_call:
        tool_name = part.function_call.name
        tool_args = dict(part.function_call.args)
        
        if tool_name == "save_requirements":
            result = save_requirements(**tool_args)
            print("\n--- REQIFY OUTPUT ---\n")
            print(tool_args["content"])
            print(f"\n✓ {result}")
    elif part.text:
        print("\n--- REQIFY OUTPUT ---\n")
        print(part.text)

# DEBUG — see exactly what Gemini returned
print("\n--- RAW RESPONSE ---")
for part in response.candidates[0].content.parts:
    if part.function_call:
        print(f"FUNCTION CALL DETECTED: {part.function_call.name}")
        print(f"ARGUMENTS: {json.dumps(dict(part.function_call.args), indent=2)}")
    elif part.text:
        print(f"TEXT: {part.text}")
print("--- END RAW ---\n")