from sqlalchemy import Column, String, DateTime, Float, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import uuid
from backend.database.postgres.base import Base

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    status = Column(String, nullable=False, default="running")
    started_at= Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    total_duration = Column(Float, nullable=True)
    best_model = Column(String, nullable=True)
    best_accuracy = Column(Float, nullable=True)
    best_metrics = Column(JSONB, nullable=True )
    error_message= Column(Text, nullable=True)