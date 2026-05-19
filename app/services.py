from app.memory.session_memory import MemoryStore
from app.retrieval.retriever import Retriever
from app.retrieval.vector_store import InMemoryVectorStore

vector_store = InMemoryVectorStore()
retriever = Retriever(vector_store)
memory_store = MemoryStore()

