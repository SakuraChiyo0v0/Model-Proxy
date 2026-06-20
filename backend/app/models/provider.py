from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, func
from app.database import Base


class ProviderModel(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), unique=True, nullable=False, index=True)
    label = Column(String(128), nullable=False)
    base_url = Column(String(512), nullable=False)
    api_path = Column(String(256), default="/v1/chat/completions")
    models_path = Column(String(256), nullable=True)   # 模型列表端点路径，None 表示不支持
    balance_path = Column(String(256), nullable=True)  # 余额查询端点路径，None 表示不支持
    enabled = Column(Boolean, default=True)
    config = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
