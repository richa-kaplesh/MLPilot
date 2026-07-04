from sqlalchemy import Column, String, DateTime, Float, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import uuid
from backend.database.postgres.base import Base

class AgentDecision(Base):
    __tablename__ = "agent_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default = uuid.uuid4)
    pipeline_run_id = Column(UUID(as_uuid=True), ForeignKey("pipeline_runs.id"), nullable = False)
    agent_name = Column(String, nullable=False)
    step_name = Column(String, nullable=False)
    decision = Column(Text, nullable=True)
    reasoning = Column(Text, nullable=True)
    alternatives_tried = Column(JSONB, nullable=True)
    outcome = Column(String, nullable=True)
    confidence_score = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())