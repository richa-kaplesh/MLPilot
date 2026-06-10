from groq import Groq
from database.vectordb.chroma import (
    get_domain_knowledge_collection,
    get_agent_experience_collection,
    get_decision_history_collection
)
from config import settings

class OrchestratorAgent:
    def __init__(self):
        self.llm = Groq(api_key=settings.groq_api_keys[0])
        self.domain_knowledge = get_domain_knowledge_collection()
        self.agent_experience = get_agent_experience_collection()
        self.decision_history = get_decision_history_collection()
    
    def analyze(self, probelm_statement: str, dataset_info: dict) -> dict:
        pass

    def delegate(self, plan: dict)->str:
        pass

    def remember(self, decision: dict, outcome: dict) -> None:
        pass
    