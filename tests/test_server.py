import pytest
from app import server


def test_extract_llamacpp_response_content():
    payload = {"choices": [{"message": {"content": "hello"}}]}
    assert server._extract_llm_text(payload, "llamacpp") == "hello"


def test_extract_ollama_response_content():
    payload = {"message": {"content": "hello"}}
    assert server._extract_llm_text(payload, "ollama") == "hello"


def test_extract_llm_text_handles_missing_fields():
    with pytest.raises(ValueError):
        server._extract_llm_text({}, "ollama")


def test_chat_raises_503_when_rag_unavailable(monkeypatch):
    monkeypatch.setattr(server, "_ensure_rag", lambda: False)

    with pytest.raises(server.HTTPException) as exc:
        server.chat(server.ChatIn(query="hi", k=2))

    assert exc.value.status_code == 503
