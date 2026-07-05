from abc import ABC, abstractmethod
from groq import Groq
from database.vectordb.chroma import get_decision_history_collection
from database.postgres.connection import get_db
from config import settings
import json
from datetime import datetime

class BaseAgent(ABC):
    def __init__(self, pipeline_run_id: str, problem_statement: str, dataset_path: str):
        self.pipeline_run_id = pipeline_run_id
        self.problem_statement = problem_statement
        self.dataset_path = dataset_path
        self.llm = Groq(api_key=settings.groq_api_keys[0])
        self.decision_history = get_decision_history_collection()

    @abstractmethod
    def run(self) -> dict:
        """Every agent must implement this — main entry point"""
        pass

    def log_decision(self, decision: str, reasoning: str, outcome: dict = None) -> None:
        """Save what this agent decided and why to ChromaDB"""
        self.decision_history.add(
            documents=[f"{decision}: {reasoning}"],
            metadatas=[{
                "pipeline_run_id": self.pipeline_run_id,
                "decision": decision,
                "outcome": json.dumps(outcome) if outcome else "",
                "timestamp": datetime.utcnow().isoformat()
            }],
            ids=[f"{self.pipeline_run_id}_{decision}_{datetime.utcnow().timestamp()}"]
        )

    def update_state(self, status: str, current_agent: str, metadata: dict = None) -> None:
        """Update pipeline state in PostgreSQL"""
        from database.postgres.connection import SessionLocal
        from database.postgres.models.pipeline_state import PipelineState        
        db = SessionLocal()
        try:
            state = db.query(PipelineState).filter(
                PipelineState.pipeline_run_id == self.pipeline_run_id
            ).first()
            
            if state:
                state.status = status
                state.current_agent = current_agent
                state.metadata = json.dumps(metadata) if metadata else None
                db.commit()
        finally:
            db.close()