from sqlalchemy.orm import Session
from app.models.route import RouteModel
from app.crypto import encrypt, decrypt


class RouteRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[RouteModel]:
        return self.db.query(RouteModel).order_by(RouteModel.created_at.desc()).all()

    def get_by_id(self, pk: int) -> RouteModel | None:
        return self.db.query(RouteModel).filter(RouteModel.id == pk).first()

    def get_by_alias(self, alias: str) -> RouteModel | None:
        return self.db.query(RouteModel).filter(RouteModel.alias == alias).first()

    def match_by_api_key(self, raw_key: str) -> RouteModel | None:
        """根据传入的 API Key 匹配路由（遍历解密对比）"""
        for route in self.db.query(RouteModel).filter(RouteModel.enabled.is_(True)).all():
            try:
                if decrypt(route.api_key) == raw_key:
                    return route
            except Exception:
                continue
        return None

    def create(self, **kwargs) -> RouteModel:
        if "api_key" in kwargs and kwargs["api_key"] is not None:
            kwargs["api_key"] = encrypt(kwargs["api_key"])
        kwargs.setdefault("model", "")
        obj = RouteModel(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, pk: int, **kwargs) -> RouteModel | None:
        obj = self.get_by_id(pk)
        if not obj:
            return None
        if "api_key" in kwargs and kwargs["api_key"] is not None:
            kwargs["api_key"] = encrypt(kwargs["api_key"])
        for k, v in kwargs.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, pk: int) -> bool:
        obj = self.get_by_id(pk)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True

    def decrypt_key(self, pk: int) -> str | None:
        obj = self.get_by_id(pk)
        if not obj or not obj.api_key:
            return None
        return decrypt(obj.api_key)
