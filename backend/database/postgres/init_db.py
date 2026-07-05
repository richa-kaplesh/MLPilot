from database.postgres.base import Base
from database.postgres.connection import engine
from database.postgres.models.dataset import Dataset
from database.postgres.models.pipeline_run import PipelineRun
from database.postgres.models.pipeline_state import PipelineState
from database.postgres.models.eda_report import EDAReport
from database.postgres.models.agent_decision import AgentDecision

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables created successfully")