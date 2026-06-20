from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    token = Column(String(128), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
