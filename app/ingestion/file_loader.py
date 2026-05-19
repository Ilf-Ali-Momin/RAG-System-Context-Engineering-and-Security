from __future__ import annotations

from pathlib import Path

from docx import Document as DocxDocument

from app.config.settings import settings
from app.ingestion.pdf_loader import extract_pdf_text
from app.models.schemas import DocumentIn
from app.security.sanitizer import sanitize_text

TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".rst"}
DOC_EXTENSIONS = {".docx"}
PDF_EXTENSIONS = {".pdf"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}


def load_documents_from_knowledge_base() -> tuple[list[DocumentIn], list[str]]:
    base_dir = Path(settings.knowledge_base_dir).expanduser().resolve()
    base_dir.mkdir(parents=True, exist_ok=True)

    documents: list[DocumentIn] = []
    indexed_paths: list[str] = []
    for path in base_dir.rglob("*"):
        if not path.is_file():
            continue
        extension = path.suffix.lower()
        document = _to_document(path, extension)
        if document is None:
            continue
        documents.append(document)
        indexed_paths.append(str(path))
    return documents, indexed_paths


def _to_document(path: Path, extension: str) -> DocumentIn | None:
    title = path.name
    source_id = f"kb::{path.relative_to(Path(settings.knowledge_base_dir).expanduser().resolve())}".replace("/", "::")
    if extension in TEXT_EXTENSIONS:
        text = sanitize_text(path.read_text(encoding="utf-8", errors="ignore"), settings.max_document_chars)
        return _doc(source_id, title, text, "text")
    if extension in PDF_EXTENSIONS:
        text = extract_pdf_text(path.read_bytes(), settings.max_document_chars)
        return _doc(source_id, title, text, "pdf")
    if extension in DOC_EXTENSIONS:
        text = _extract_docx(path)
        return _doc(source_id, title, text, "docx")
    if extension in VIDEO_EXTENSIONS:
        text = _extract_video_text(path)
        return _doc(source_id, title, text, "video")
    return None


def _extract_docx(path: Path) -> str:
    doc = DocxDocument(str(path))
    text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
    return sanitize_text(text, settings.max_document_chars)


def _extract_video_text(path: Path) -> str:
    sidecar_txt = path.with_suffix(".txt")
    sidecar_md = path.with_suffix(".md")
    transcript = ""
    if sidecar_txt.exists():
        transcript = sidecar_txt.read_text(encoding="utf-8", errors="ignore")
    elif sidecar_md.exists():
        transcript = sidecar_md.read_text(encoding="utf-8", errors="ignore")

    stats = path.stat()
    info = (
        f"Video file: {path.name}\n"
        f"Size bytes: {stats.st_size}\n"
        f"Last modified: {stats.st_mtime}\n"
        f"Transcript:\n{transcript}"
    )
    return sanitize_text(info, settings.max_document_chars)


def _doc(source_id: str, title: str, text: str, file_type: str) -> DocumentIn | None:
    if not text.strip():
        return None
    return DocumentIn(
        source_id=source_id,
        title=title,
        content=text,
        trust_level=4,
        metadata={"file_type": file_type, "source": "knowledge_base"},
    )

