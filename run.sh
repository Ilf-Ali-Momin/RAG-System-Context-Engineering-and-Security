#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama CLI not found. Install from https://ollama.com and re-run."
  exit 1
fi

OLLAMA_BASE_URL="${RAG_OLLAMA_BASE_URL:-http://localhost:11434}"
CHAT_MODEL="${RAG_OLLAMA_CHAT_MODEL:-llama3.1:8b}"
EMBED_MODEL="${RAG_OLLAMA_EMBEDDING_MODEL:-nomic-embed-text}"
APP_HOST="${RAG_APP_HOST:-127.0.0.1}"
APP_PORT="${RAG_APP_PORT:-8000}"

if ! curl -fsS "${OLLAMA_BASE_URL}/api/tags" >/dev/null 2>&1; then
  echo "Starting Ollama server..."
  ollama serve >/tmp/ollama.log 2>&1 &
  for _ in {1..20}; do
    sleep 1
    if curl -fsS "${OLLAMA_BASE_URL}/api/tags" >/dev/null 2>&1; then
      break
    fi
  done
fi

if ! curl -fsS "${OLLAMA_BASE_URL}/api/tags" >/dev/null 2>&1; then
  echo "Could not reach Ollama at ${OLLAMA_BASE_URL}."
  echo "Check /tmp/ollama.log for details."
  exit 1
fi

echo "Ensuring Ollama models are available..."
ollama pull "${CHAT_MODEL}"
ollama pull "${EMBED_MODEL}"

export RAG_OLLAMA_BASE_URL="${OLLAMA_BASE_URL}"
export RAG_OLLAMA_CHAT_MODEL="${CHAT_MODEL}"
export RAG_OLLAMA_EMBEDDING_MODEL="${EMBED_MODEL}"

if curl -fsS "http://${APP_HOST}:${APP_PORT}/health" >/dev/null 2>&1; then
  echo "API already running at http://${APP_HOST}:${APP_PORT}."
  echo "Open http://${APP_HOST}:${APP_PORT}/ui"
  exit 0
fi

echo "Starting API at http://${APP_HOST}:${APP_PORT} ..."
exec uvicorn app.main:app --reload --host "${APP_HOST}" --port "${APP_PORT}"

