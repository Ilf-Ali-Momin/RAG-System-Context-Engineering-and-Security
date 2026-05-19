from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAG_", env_file=".env", extra="ignore")

    max_user_query_chars: int = 4000
    max_document_chars: int = 50000
    retrieval_top_k: int = 8
    max_context_chunks: int = 6
    max_context_chars: int = 6000
    min_similarity: float = 0.15
    min_context_confidence: float = 0.45
    dedupe_similarity_threshold: float = 0.92
    blocked_pattern_score_threshold: int = 2
    allow_model_fallback_answering: bool = False
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.1:8b"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_request_timeout_seconds: float = 30.0
    ollama_embeddings_enabled: bool = True
    knowledge_base_dir: str = "./knowledge_base"


settings = Settings()

