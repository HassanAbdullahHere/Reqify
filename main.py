from google import genai
from dotenv import load_dotenv


load_dotenv()
client = genai.Client()

brief = input("Paste your client brief: ")

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=f"Extract requirements from this client brief: {brief}"
)
print(response.text)
