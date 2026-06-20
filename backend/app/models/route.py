from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.database import Base


class RouteModel(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alias = Column(String(128), unique=True, nullable=False, index=True)   # 名称，如 "我的OpenAI"
    provider_id = Column(Integer, nullable=False, index=True)              # 绑定的厂商
    api_key = Column(String(512), nullable=False)                          # 路由专属 Key（加密）
    model = Column(String(128), nullable=False, default="")                 # 绑定的模型
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
