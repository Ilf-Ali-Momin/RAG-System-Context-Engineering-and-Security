from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.chat import router as chat_router
from app.api.ingest import router as ingest_router
from app.integrations.ollama_health import ollama_health_status

app = FastAPI(title="Secure Context-Engineered RAG MVP", version="0.1.0")
app.include_router(ingest_router)
app.include_router(chat_router)
UI_FILE = Path(__file__).resolve().parent / "ui" / "index.html"


@app.get("/")
def root() -> dict[str, object]:
    return {
        "name": "Secure Context-Engineered RAG MVP",
        "status": "ok",
        "endpoints": ["/health", "/health/ollama", "/ingest", "/ingest/pdf", "/ingest/sync", "/chat", "/ui"],
    }


@app.get("/ui")
def ui() -> FileResponse:
    return FileResponse(UI_FILE)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ollama")
def health_ollama() -> dict[str, object]:
    return ollama_health_status()

