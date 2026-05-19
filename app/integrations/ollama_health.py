from __future__ import annotations

import httpx

from app.config.settings import settings


def ollama_health_status() -> dict[str, object]:
    configured = {
        "base_url": settings.ollama_base_url,
        "chat_model": settings.ollama_chat_model,
        "embedding_model": settings.ollama_embedding_model,
    }
    try:
        with httpx.Client(timeout=settings.ollama_request_timeout_seconds) as client:
            response = client.get(f"{settings.ollama_base_url}/api/tags")
            response.raise_for_status()
            payload = response.json()
    except Exception as exc:
        return {
            "status": "degraded",
            "reachable": False,
            "configured": configured,
            "chat_model_available": False,
            "embedding_model_available": False,
            "error": str(exc),
        }

    models = payload.get("models", [])
    available_model_names = {model.get("name", "") for model in models if isinstance(model, dict)}
    chat_model_available = settings.ollama_chat_model in available_model_names
    embedding_model_available = settings.ollama_embedding_model in available_model_names
    status = "ok" if chat_model_available and embedding_model_available else "degraded"
    return {
        "status": status,
        "reachable": True,
        "configured": configured,
        "chat_model_available": chat_model_available,
        "embedding_model_available": embedding_model_available,
        "available_models": sorted(available_model_names),
    }

