from google import genai
import os

from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
stream = client.models.generate_content_stream(
    model="gemini-2.5-flash-lite",
    contents="Connection Check!",
)

for chunk in stream:
    print(chunk.text, end="", flush=True)
# print(response.text)