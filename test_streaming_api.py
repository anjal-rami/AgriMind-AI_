import pytest
from fastapi.testclient import TestClient
from app import app, CHAT_SESSIONS

client = TestClient(app)

def test_chat_endpoints():
    session_id = "test_session_123"

    # Reset session first
    reset_resp = client.delete(f"/api/v1/chat/reset/{session_id}")
    assert reset_resp.status_code == 200
    assert reset_resp.json()["status"] == "success"

    # Test Stream endpoint
    stream_resp = client.post(
        "/api/v1/chat/stream",
        json={"session_id": session_id, "message": "Give 1 tip for wheat irrigation."}
    )
    assert stream_resp.status_code == 200
    token_stream = stream_resp.text
    print("Streamed content length:", len(token_stream))
    print("Streamed sample:", token_stream[:150])
    assert len(token_stream) > 0

    # Test History endpoint
    hist_resp = client.get(f"/api/v1/chat/history/{session_id}")
    assert hist_resp.status_code == 200
    history = hist_resp.json()["history"]
    print("History turns:", len(history))
    assert len(history) == 2  # 1 user, 1 assistant
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"

    print("All streaming & session history tests PASSED!")

if __name__ == "__main__":
    test_chat_endpoints()
