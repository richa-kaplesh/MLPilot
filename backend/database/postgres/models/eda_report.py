from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import uuid
from database.postgres.base import Base
class EDAReport(Base):
    __tablename__ = "eda_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    missing_values = Column(JSONB, nullable=True)
    data_types = Column(JSONB, nullable=True)
    correlations = Column(JSONB, nullable=True)
    skewness = Column(JSONB, nullable=True)
    normality = Column(JSONB, nullable=True)
    feature_importance = Column(JSONB, nullable=True)
    outliers = Column(JSONB, nullable = True)
    class_balance = Column(JSONB, nullable=True)
    summary = Column(Text, nullable=True)
    created_At = Column(DateTime(timezone=True), server_default=func.now())
    target_column = Column(String, nullable=True)
    target_analysis = Column(JSONB, nullable=True)