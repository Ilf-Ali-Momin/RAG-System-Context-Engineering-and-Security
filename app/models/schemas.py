from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class DocumentIn(BaseModel):
    source_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    trust_level: int = Field(default=3, ge=1, le=5)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestRequest(BaseModel):
    documents: list[DocumentIn] = Field(default_factory=list)


class IngestResponse(BaseModel):
    accepted_documents: int
    created_chunks: int
    indexed_files: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1, max_length=4000)
    top_k: int = Field(default=8, ge=1, le=30)


class Citation(BaseModel):
    source_id: str
    title: str
    chunk_id: str


class ChatResponse(BaseModel):
    status: Literal["answer", "refusal"]
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    reason: str | None = None


class ChunkRecord(BaseModel):
    chunk_id: str
    source_id: str
    title: str
    text: str
    trust_level: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    chunk: ChunkRecord
    similarity: float
    quality_score: float = 0.0
    security_flags: list[str] = Field(default_factory=list)

