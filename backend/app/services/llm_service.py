from urllib import response

import requests
import os

from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/chat"

MODEL_NAME = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:8b"
)

def generate_response(
    message: str,
    system_prompt: str | None = None
) -> str:

    if system_prompt is None:
        system_prompt = """
        You are a friendly customer support assistant for an online store.

        Respond naturally, like a helpful human support agent.

        Rules:
        - Keep answers concise and conversational.
        - Do not use headings or long bullet lists unless they are genuinely useful.
        - Do not use Markdown formatting such as **bold**, *italics*, headings, or bullet symbols unless explicitly requested.
        - Do not repeat the user's question.
        - Avoid overly formal or robotic wording.
        - Do not invent store policies, prices, deadlines, fees, or product details.
        - If information is not available, say that you do not have that information.
        - Ask a short follow-up question when it would help the customer.
        """

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"]