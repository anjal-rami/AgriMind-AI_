import os
from typing import AsyncGenerator, Dict, List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_NVIDIA_API_KEY = "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"

# Setup client using NVIDIA NIM endpoint
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY") or DEFAULT_NVIDIA_API_KEY
)

# Active models on NVIDIA NIM:
# - "meta/llama-3.2-11b-vision-instruct"
# - "meta/llama-3.2-90b-vision-instruct"
# - "nvidia/llama-3.1-nemotron-70b-instruct"
DEFAULT_MODEL = os.getenv("NVIDIA_MODEL", "meta/llama-3.2-11b-vision-instruct")

AGRIMIND_SYSTEM_PROMPT = (
    "You are the core AI Advisor for AgriMind AI, a multi-agent agriculture intelligence platform. "
    "Provide clear, actionable, and scientific guidance on crop health, soil preparation, "
    "irrigation, and fertilizer usage. Where relevant, suggest consulting local agronomy experts."
)

def generate_chat_response(messages: List[Dict[str, str]]) -> str:
    """Synchronous single-turn/multi-turn response."""
    payload = [{"role": "system", "content": AGRIMIND_SYSTEM_PROMPT}] + messages
    
    completion = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=payload,
        temperature=0.3,
        max_tokens=1024,
    )
    return completion.choices[0].message.content

def stream_chat_response(messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
    """Generator for streaming responses directly to the farmer dashboard."""
    payload = [{"role": "system", "content": AGRIMIND_SYSTEM_PROMPT}] + messages
    
    stream = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=payload,
        temperature=0.3,
        max_tokens=1024,
        stream=True
    )
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content
