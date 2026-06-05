from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import uuid
from database.postgres.base import Base

class EDAReport(Base):
    __tablename__ = "eda_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    row_count = Column(String, nullable=True)
    column_count = Column(String, nullable=True)
    missing_values = Column(JSONB, nullable=True)
    data_types = Column(JSONB, nullable=True)
    correlations = Column(JSONB, nullable=True)
    skewness = Column(JSONB, nullable=True)
    feature_importance = Column(JSONB, nullable=True)
    outliers = Column(JSONB)