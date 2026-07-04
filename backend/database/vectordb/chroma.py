import chromadb
from config import settings

_client = None

def get_chroma_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory
        )
    return _client

def get_domain_knowledge_collection():
    return get_chroma_client().get_or_create_collection(
        name="domain_knowledge",
        metadata={"description": "ML domain knowledge and best practices"}
    )

def get_agent_experience_collection():
    return get_chroma_client().get_or_create_collection(
        name="agent_experience",
        metadata={"description": "Past agent actions and what they led to"}
    )

def get_decision_history_collection():
    return get_chroma_client().get_or_create_collection(
        name="decision_history",
        metadata={"description": "Specific decisions made and their outcomes"}
    )
