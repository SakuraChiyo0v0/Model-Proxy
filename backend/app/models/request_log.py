from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from app.database import Base


class RequestLogModel(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    model = Column(String(128), nullable=True)
    request_body = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    error_message = Column(String(1024), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
