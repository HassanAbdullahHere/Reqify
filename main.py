from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

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
"""

brief = input("Paste your client brief: ")

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[
        {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
        {"role": "model", "parts": [{"text": "Understood. Send me the client brief."}]},
        {"role": "user", "parts": [{"text": brief}]}
    ]
)

print("\n--- REQIFY OUTPUT ---\n")
print(response.text)