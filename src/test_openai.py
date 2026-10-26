import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("ERROR: API key not found in .env")
    exit()

try:
    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input="Explain Instamart Copilot in two simple sentences."
    )

    print("\nSUCCESS!")
    print(response.output_text)

except Exception as e:
    print("\nAPI REQUEST FAILED")
    print("Error type:", type(e).__name__)
    print("Error details:", str(e))