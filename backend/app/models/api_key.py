from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from app.database import Base


class ApiKeyModel(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    alias = Column(String(64), default="")
    key_value = Column(String(512), nullable=False)   # AES encrypted
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
