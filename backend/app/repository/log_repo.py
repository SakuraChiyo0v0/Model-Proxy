from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.request_log import RequestLogModel


class LogRepo:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> RequestLogModel:
        obj = RequestLogModel(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_all(self, skip: int = 0, limit: int = 50, provider_id: int | None = None) -> tuple[list[RequestLogModel], int]:
        q = self.db.query(RequestLogModel)
        if provider_id is not None:
            q = q.filter(RequestLogModel.provider_id == provider_id)
        total = q.count()
        rows = q.order_by(desc(RequestLogModel.created_at)).offset(skip).limit(limit).all()
        return rows, total

    def get_by_id(self, pk: int) -> RequestLogModel | None:
        return self.db.query(RequestLogModel).filter(RequestLogModel.id == pk).first()
