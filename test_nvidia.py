# test_nvidia.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

# Active models on NVIDIA NIM: meta/llama-3.2-11b-vision-instruct, meta/llama-3.2-90b-vision-instruct, nvidia/llama-3.1-nemotron-70b-instruct
model_to_use = os.getenv("NVIDIA_MODEL", "meta/llama-3.2-11b-vision-instruct")

response = client.chat.completions.create(
    model=model_to_use,
    messages=[
        {"role": "user", "content": "Briefly state 3 key soil nutrients needed for wheat growth."}
    ],
    temperature=0.2,
    max_tokens=100
)

print(f"Status: Connected successfully! (Model: {model_to_use})")
print("Response:\n", response.choices[0].message.content)
