from database.postgres.base import Base
from database.postgres.connection import engine
from models.database.dataset import Dataset
from models.database.pipeline_run import PipelineRun
from models.database.pipeline_state import PipelineState
from models.database.eda_report import EDAReport
from models.database.agent_decision import AgentDecision

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "main":
    init_db()
    print("Database tables created successfully")