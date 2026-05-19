from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config.settings import settings
from app.ingestion.chunker import chunk_document
from app.ingestion.file_loader import load_documents_from_knowledge_base
from app.ingestion.loaders import normalize_documents
from app.ingestion.pdf_loader import extract_pdf_text
from app.models.schemas import DocumentIn, IngestRequest, IngestResponse
from app.services import vector_store

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("", response_model=IngestResponse)
def ingest_documents(payload: IngestRequest) -> IngestResponse:
    docs = normalize_documents(payload.documents, max_chars=settings.max_document_chars)
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc))
    vector_store.add_chunks(all_chunks)
    return IngestResponse(accepted_documents=len(docs), created_chunks=len(all_chunks), indexed_files=[])


@router.post("/pdf", response_model=IngestResponse)
async def ingest_pdfs(
    files: list[UploadFile] = File(...),
    trust_level: int = Form(default=4),
) -> IngestResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No PDF files provided.")
    if trust_level < 1 or trust_level > 5:
        raise HTTPException(status_code=400, detail="trust_level must be between 1 and 5.")

    docs: list[DocumentIn] = []
    for idx, file in enumerate(files):
        if file.content_type not in {"application/pdf", "application/x-pdf"}:
            raise HTTPException(status_code=400, detail=f"Unsupported file type for {file.filename}.")
        data = await file.read()
        if not data:
            continue
        text = extract_pdf_text(data, max_chars=settings.max_document_chars)
        if not text.strip():
            continue
        source_id = f"pdf-{idx}-{(file.filename or 'document').replace(' ', '_')}"
        docs.append(
            DocumentIn(
                source_id=source_id,
                title=file.filename or f"PDF {idx + 1}",
                content=text,
                trust_level=trust_level,
                metadata={"file_type": "pdf"},
            )
        )

    docs = normalize_documents(docs, max_chars=settings.max_document_chars)
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc))
    vector_store.add_chunks(all_chunks)
    return IngestResponse(accepted_documents=len(docs), created_chunks=len(all_chunks), indexed_files=[])


@router.post("/sync", response_model=IngestResponse)
def sync_knowledge_base() -> IngestResponse:
    docs, indexed_files = load_documents_from_knowledge_base()
    docs = normalize_documents(docs, max_chars=settings.max_document_chars)
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc))
    vector_store.add_chunks(all_chunks)
    return IngestResponse(
        accepted_documents=len(docs),
        created_chunks=len(all_chunks),
        indexed_files=indexed_files,
    )

