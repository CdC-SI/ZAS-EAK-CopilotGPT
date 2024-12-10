from unittest.mock import patch

with patch("sqlalchemy.create_engine") as mock_engine:
    from fastapi.testclient import TestClient
    from app.settings_api import app
    from app.config.llm_config import (
        SUPPORTED_OPENAI_LLM_MODELS,
        SUPPORTED_AZUREOPENAI_LLM_MODELS,
        SUPPORTED_ANTHROPIC_LLM_MODELS,
        SUPPORTED_GEMINI_LLM_MODELS,
        SUPPORTED_GROQ_LLM_MODELS,
        SUPPORTED_MLX_LLM_MODELS,
        SUPPORTED_LLAMACPP_LLM_MODELS,
        SUPPORTED_OLLAMA_LLM_MODELS,
    )

client = TestClient(app)


def test_llm_models():
    response = client.get("/llm_models")
    assert response.status_code == 200
    expected_models = (
        SUPPORTED_OPENAI_LLM_MODELS
        + SUPPORTED_AZUREOPENAI_LLM_MODELS
        + SUPPORTED_ANTHROPIC_LLM_MODELS
        + SUPPORTED_GEMINI_LLM_MODELS
        + SUPPORTED_GROQ_LLM_MODELS
        + SUPPORTED_MLX_LLM_MODELS
        + SUPPORTED_LLAMACPP_LLM_MODELS
        + SUPPORTED_OLLAMA_LLM_MODELS
    )
    assert response.json() == expected_models


def test_retrieval_methods():
    response = client.get("/retrieval_methods")
    assert response.status_code == 200
    expected_methods = [
        "top_k_retriever",
        "query_rewriting_retriever",
        "contextual_compression_retriever",
        "rag_fusion_retriever",
        "bm25",
        "reranking",
    ]
    assert response.json() == expected_methods
