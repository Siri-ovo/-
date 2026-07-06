import pytest

from src.llm.career_advisor import call_ollama_with_fallback


def test_call_ollama_with_fallback_tries_next_model():
    calls = []

    def fake_call(prompt, model, base_url):
        calls.append(model)
        if model == "qwen3:4b":
            raise RuntimeError("model failed")
        return {"recommendations": [{"title": "Data Analyst", "llm_score": 80}]}

    result = call_ollama_with_fallback(
        "prompt",
        models=["qwen3:4b", "qwen2:0.5b"],
        caller=fake_call,
    )

    assert calls == ["qwen3:4b", "qwen2:0.5b"]
    assert result["model_used"] == "qwen2:0.5b"
    assert result["report"]["recommendations"][0]["title"] == "Data Analyst"


def test_call_ollama_with_fallback_raises_last_error():
    def fake_call(prompt, model, base_url):
        raise RuntimeError(f"{model} failed")

    with pytest.raises(RuntimeError, match="qwen2:0.5b failed"):
        call_ollama_with_fallback("prompt", models=["qwen3:4b", "qwen2:0.5b"], caller=fake_call)
