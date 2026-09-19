# app.py
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel, Field

from agri_guardrail import MandatoryRuleGuard

load_dotenv()

app = FastAPI(title="AgriMind AI Backend API with Mandatory Guardrails")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Guardrail
guard = MandatoryRuleGuard("rules/agri_rules.json")

# Initialize NVIDIA NIM client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
)

MODEL_NAME = os.getenv("NVIDIA_MODEL", "meta/llama-3.3-70b-instruct")

# In-memory store: {session_id: [messages]}
CHAT_SESSIONS: Dict[str, List[Dict[str, str]]] = {}


class FarmQuery(BaseModel):
    session_id: str = "default_session"
    user_prompt: str
    telemetry: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ChatStreamRequest(BaseModel):
    session_id: str
    message: str
    telemetry: Optional[Dict[str, Any]] = Field(default_factory=dict)


def build_guarded_system_instruction(telemetry: Dict[str, Any]):
    # STEP 1: PERMANENT RULE EVALUATION (Always runs first)
    overrides, mandatory_directives = guard.evaluate_and_enforce(telemetry)
    telemetry.update(overrides)

    # STEP 2: BUILD STRICT CONTEXT INJECTION
    rules_context = "\n".join(mandatory_directives) if mandatory_directives else "All sensor metrics within nominal thresholds."

    system_instruction = f"""You are AgriMind AI, a multi-agent decision support platform.
You operate under a strict, mandatory agronomic Rule Engine.

ACTIVE SYSTEM RULES & DETERMINISTIC OVERRIDES:
{rules_context}

CRITICAL OPERATIONAL DIRECTIVE:
You CANNOT contradict, relax, or override the active rules above. 
If an override is active (such as HALT_IRRIGATION), you must base your entire advisory around that fact, explaining the exact agronomic reason to the farmer."""

    return system_instruction, overrides, mandatory_directives


@app.post("/api/v1/chat")
async def guarded_chat(payload: FarmQuery):
    telemetry = payload.telemetry or {}
    system_instruction, overrides, mandatory_directives = build_guarded_system_instruction(telemetry)

    # STEP 3: EXECUTE NVIDIA NIM LLM
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": payload.user_prompt}
        ],
        temperature=0.2
    )

    reply_content = response.choices[0].message.content if response.choices else ""

    # Retain session memory
    if payload.session_id not in CHAT_SESSIONS:
        CHAT_SESSIONS[payload.session_id] = [{"role": "system", "content": system_instruction}]
    CHAT_SESSIONS[payload.session_id].append({"role": "user", "content": payload.user_prompt})
    CHAT_SESSIONS[payload.session_id].append({"role": "assistant", "content": reply_content})

    return {
        "reply": reply_content,
        "enforced_rules": mandatory_directives,
        "active_overrides": overrides
    }


def generate_nvidia_stream(session_id: str, prompt: str, telemetry: Dict[str, Any]):
    system_instruction, _, _ = build_guarded_system_instruction(telemetry)

    if session_id not in CHAT_SESSIONS:
        CHAT_SESSIONS[session_id] = [{"role": "system", "content": system_instruction}]

    CHAT_SESSIONS[session_id].append({"role": "user", "content": prompt})
    history_window = [CHAT_SESSIONS[session_id][0]] + CHAT_SESSIONS[session_id][-10:]

    stream = client.chat.completions.create(
        model=MODEL_NAME,
        messages=history_window,
        temperature=0.3,
        max_tokens=1024,
        stream=True,
    )

    full_response = ""
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            full_response += delta
            yield delta

    CHAT_SESSIONS[session_id].append({"role": "assistant", "content": full_response})


@app.post("/api/v1/chat/stream")
async def chat_stream_endpoint(payload: ChatStreamRequest):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    return StreamingResponse(
        generate_nvidia_stream(payload.session_id, payload.message, payload.telemetry or {}),
        media_type="text/plain",
    )


@app.get("/api/v1/chat/history/{session_id}")
async def get_history(session_id: str):
    """Fetch stored conversation turns for a given session."""
    history = CHAT_SESSIONS.get(session_id, [])
    return {
        "session_id": session_id,
        "history": [msg for msg in history if msg["role"] != "system"],
    }


@app.delete("/api/v1/chat/reset/{session_id}")
async def reset_session(session_id: str):
    """Clear memory for a new chat."""
    if session_id in CHAT_SESSIONS:
        CHAT_SESSIONS.pop(session_id, None)
    return {"status": "success", "message": f"Session {session_id} reset."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
