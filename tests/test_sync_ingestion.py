from pathlib import Path

from fastapi.testclient import TestClient

from app.config.settings import settings
from app.main import app

client = TestClient(app)


def test_sync_knowledge_base_ingests_text_and_video_sidecar(tmp_path: Path) -> None:
    kb = tmp_path / "knowledge_base"
    kb.mkdir(parents=True, exist_ok=True)
    (kb / "notes.txt").write_text("Context engineering keeps only relevant trusted chunks.", encoding="utf-8")
    (kb / "lesson.mp4").write_bytes(b"fake")
    (kb / "lesson.txt").write_text("Video transcript about prompt injection defense.", encoding="utf-8")

    old_dir = settings.knowledge_base_dir
    try:
        settings.knowledge_base_dir = str(kb)
        response = client.post("/ingest/sync")
        payload = response.json()
    finally:
        settings.knowledge_base_dir = old_dir
    assert response.status_code == 200
    assert payload["accepted_documents"] >= 2
    assert payload["created_chunks"] >= 2
    assert any("notes.txt" in path for path in payload["indexed_files"])

