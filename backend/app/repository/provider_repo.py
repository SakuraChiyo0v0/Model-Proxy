from sqlalchemy.orm import Session
from app.models.provider import ProviderModel
from app.models.api_key import ApiKeyModel
from app.crypto import encrypt, decrypt


class ProviderRepo:
    def __init__(self, db: Session):
        self.db = db

    # ── Provider ───────────────────────

    def get_all(self) -> list[ProviderModel]:
        return self.db.query(ProviderModel).all()

    def get_by_id(self, pk: int) -> ProviderModel | None:
        return self.db.query(ProviderModel).filter(ProviderModel.id == pk).first()

    def get_by_name(self, name: str) -> ProviderModel | None:
        return self.db.query(ProviderModel).filter(ProviderModel.name == name).first()

    def match_by_model(self, model: str) -> ProviderModel | None:
        p = self.db.query(ProviderModel).filter(
            ProviderModel.name == model, ProviderModel.enabled.is_(True)
        ).first()
        if p and self._has_key(p.id):
            return p
        all_enabled = self.db.query(ProviderModel).filter(ProviderModel.enabled.is_(True)).all()
        for p in all_enabled:
            if self._has_key(p.id) and model.lower().startswith(p.name.lower()):
                return p
        return None

    def create(self, **kwargs) -> ProviderModel:
        obj = ProviderModel(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, pk: int, **kwargs) -> ProviderModel | None:
        obj = self.get_by_id(pk)
        if not obj:
            return None
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
        # delete associated keys first
        self.db.query(ApiKeyModel).filter(ApiKeyModel.provider_id == pk).delete()
        self.db.delete(obj)
        self.db.commit()
        return True

    # ── API Keys ───────────────────────

    def _has_key(self, provider_id: int) -> bool:
        return self.db.query(ApiKeyModel).filter(
            ApiKeyModel.provider_id == provider_id, ApiKeyModel.enabled.is_(True)
        ).first() is not None

    def get_keys(self, provider_id: int) -> list[ApiKeyModel]:
        return self.db.query(ApiKeyModel).filter(ApiKeyModel.provider_id == provider_id).all()

    def get_first_key(self, provider_id: int) -> ApiKeyModel | None:
        return self.db.query(ApiKeyModel).filter(
            ApiKeyModel.provider_id == provider_id, ApiKeyModel.enabled.is_(True)
        ).first()

    def add_key(self, provider_id: int, alias: str, key_value: str) -> ApiKeyModel:
        obj = ApiKeyModel(
            provider_id=provider_id, alias=alias,
            key_value=encrypt(key_value)
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_key(self, pk: int) -> ApiKeyModel | None:
        return self.db.query(ApiKeyModel).filter(ApiKeyModel.id == pk).first()

    def update_key(self, pk: int, **kwargs) -> ApiKeyModel | None:
        obj = self.get_key(pk)
        if not obj:
            return None
        if "key_value" in kwargs and kwargs["key_value"] is not None:
            kwargs["key_value"] = encrypt(kwargs["key_value"])
        for k, v in kwargs.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_key(self, pk: int) -> bool:
        obj = self.get_key(pk)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True

    def decrypt_key(self, pk: int) -> str | None:
        obj = self.get_key(pk)
        if not obj or not obj.key_value:
            return None
        return decrypt(obj.key_value)
