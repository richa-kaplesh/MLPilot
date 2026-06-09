import chromadb
from chromadb.settings import Settings
from config import settings

client = chromadb.PersistentClient(
    path=settings.chroma_persist_directory
)

def get_domain_knowledge_collection():
    return client.get_or_create_collection(
        name="domain_knowledge",
        metadata={"description": "Ml domain knowledge and best practices"}
    )

def get_agent_experience_collection():
    return client.get_or_create_collection(
        name="decision_history",
        metadata={"description":"Past decisions and their outcomes"}
    )