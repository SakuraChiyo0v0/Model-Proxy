from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.repository import ProviderRepo, LogRepo, UserRepo, pwd_context
from app.repository.route_repo import RouteRepo
from app.services.proxy_service import AuthService
from app.templates import PROVIDER_TEMPLATES
from app.providers.registry import ProviderRegistry

router = APIRouter(prefix="/api/admin")

security = HTTPBearer(auto_error=False)


def require_admin(creds: HTTPAuthorizationCredentials = Depends(security),
                  db: Session = Depends(get_db)) -> str:
    expected = AuthService.get_admin_token(db)
    if not creds or not expected or creds.credentials != expected:
        raise HTTPException(401, "Invalid token")
    return "admin"


# ── Auth ───────────────────────────────────────────

class LoginBody(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(body: LoginBody, db: Session = Depends(get_db)):
    user = UserRepo(db).get_by_username(body.username)
    if not user or not pwd_context.verify(body.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return {"token": AuthService.create_admin_token(db)}


# ── Templates ───────────────────────────────────────

@router.get("/provider-templates")
def list_templates():
    return PROVIDER_TEMPLATES


@router.get("/provider-templates/{name}")
def get_template(name: str):
    for t in PROVIDER_TEMPLATES:
        if t["name"] == name:
            return t
    raise HTTPException(404, "Template not found")


# ── Providers ──────────────────────────────────────

class ProviderCreateBody(BaseModel):
    name: str
    label: str
    base_url: str
    api_path: str = "/v1/chat/completions"
    key_value: str


class TemplateCreateBody(BaseModel):
    template_name: str
    key_value: str


class ProviderUpdateBody(BaseModel):
    label: str | None = None
    base_url: str | None = None
    api_path: str | None = None
    models_path: str | None = None
    balance_path: str | None = None
    enabled: bool | None = None


@router.get("/providers")
def list_providers(db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    repo = ProviderRepo(db)
    rows = repo.get_all()
    return [{
        "id": r.id, "name": r.name, "label": r.label,
        "base_url": r.base_url, "api_path": r.api_path,
        "models_path": r.models_path, "balance_path": r.balance_path,
        "enabled": r.enabled, "key_count": len(repo.get_keys(r.id)),
        "created_at": str(r.created_at)
    } for r in rows]


@router.post("/providers")
def create_provider(body: ProviderCreateBody, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    repo = ProviderRepo(db)
    if repo.get_by_name(body.name):
        raise HTTPException(400, "Provider already exists")
    obj = repo.create(name=body.name, label=body.label, base_url=body.base_url, api_path=body.api_path)
    repo.add_key(obj.id, "default", body.key_value)
    return {"id": obj.id, "name": obj.name, "label": obj.label}


@router.post("/providers/from-template")
def create_from_template(body: TemplateCreateBody, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    tmpl = next((t for t in PROVIDER_TEMPLATES if t["name"] == body.template_name), None)
    if not tmpl:
        raise HTTPException(400, "Template not found")
    repo = ProviderRepo(db)
    if repo.get_by_name(tmpl["name"]):
        raise HTTPException(400, f"Provider '{tmpl['label']}' already exists")
    obj = repo.create(
        name=tmpl["name"], label=tmpl["label"],
        base_url=tmpl["base_url"], api_path=tmpl["api_path"],
        models_path=tmpl.get("models_path"),
        balance_path=tmpl.get("balance_path"),
    )
    repo.add_key(obj.id, "default", body.key_value)
    return {"id": obj.id, "name": obj.name, "label": obj.label}


@router.put("/providers/{pk}")
def update_provider(pk: int, body: ProviderUpdateBody, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(400, "No fields to update")
    obj = ProviderRepo(db).update(pk, **updates)
    if not obj:
        raise HTTPException(404, "Provider not found")
    return {"id": obj.id, "name": obj.name, "label": obj.label}


@router.delete("/providers/{pk}")
def delete_provider(pk: int, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    if not ProviderRepo(db).delete(pk):
        raise HTTPException(404, "Provider not found")
    return {"ok": True}


# ── API Keys (per provider) ────────────────────────

class AddKeyBody(BaseModel):
    alias: str = ""
    key_value: str


class UpdateKeyBody(BaseModel):
    alias: str | None = None
    key_value: str | None = None
    enabled: bool | None = None


@router.get("/providers/{pk}/keys")
def list_keys(pk: int, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    repo = ProviderRepo(db)
    if not repo.get_by_id(pk):
        raise HTTPException(404, "Provider not found")
    keys = repo.get_keys(pk)
    return [{"id": k.id, "alias": k.alias, "enabled": k.enabled,
             "created_at": str(k.created_at)} for k in keys]


@router.post("/providers/{pk}/keys")
def add_key(pk: int, body: AddKeyBody, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    repo = ProviderRepo(db)
    if not repo.get_by_id(pk):
        raise HTTPException(404, "Provider not found")
    obj = repo.add_key(pk, body.alias, body.key_value)
    return {"id": obj.id, "key_value": body.key_value}


@router.put("/providers/{pk}/keys/{kid}")
def update_key(pk: int, kid: int, body: UpdateKeyBody, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    repo = ProviderRepo(db)
    key = repo.get_key(kid)
    if not key or key.provider_id != pk:
        raise HTTPException(404, "Key not found")
    updates = body.model_dump(exclude_none=True)
    obj = repo.update_key(kid, **updates)
    return {"id": obj.id, "alias": obj.alias, "enabled": obj.enabled}


@router.delete("/providers/{pk}/keys/{kid}")
def delete_key(pk: int, kid: int, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    repo = ProviderRepo(db)
    key = repo.get_key(kid)
    if not key or key.provider_id != pk:
        raise HTTPException(404, "Key not found")
    # 至少保留一个 Key
    active_keys = [k for k in repo.get_keys(pk) if k.id != kid]
    if not active_keys:
        raise HTTPException(400, "Cannot delete the last API key")
    repo.delete_key(kid)
    return {"ok": True}


# ── Test & Balance ─────────────────────────────

class TestConnectBody(BaseModel):
    template_name: str
    key_value: str
    custom_base_url: str | None = None  # 用于路由管理的自定义地址测试


@router.post("/providers/test")
async def test_connectivity(body: TestConnectBody, _admin: str = Depends(require_admin)):
    tmpl = next((t for t in PROVIDER_TEMPLATES if t["name"] == body.template_name), None)
    if not tmpl:
        raise HTTPException(400, "Template not found")
    base_url = body.custom_base_url or tmpl["base_url"]
    adapter = ProviderRegistry.get(tmpl["name"])
    ok, msg = await adapter.test_connectivity(base_url, tmpl["api_path"], body.key_value)
    return {"ok": ok, "message": msg}


@router.get("/providers/{pk}/models")
async def list_models(pk: int, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    """获取厂商可用模型列表"""
    repo = ProviderRepo(db)
    provider = repo.get_by_id(pk)
    if not provider:
        raise HTTPException(404, "Provider not found")
    key = repo.get_first_key(pk)
    if not key:
        return {"models": []}
    api_key = repo.decrypt_key(key.id)
    if not api_key:
        return {"models": []}
    adapter = ProviderRegistry.get(provider.name)
    if adapter is None:
        from app.providers.base import DefaultProvider
        adapter = DefaultProvider()
    models = await adapter.list_models(
        provider.base_url, provider.api_path, api_key,
        models_path=provider.models_path,
    )
    return {"models": models}


@router.get("/providers/{pk}/balance")
async def get_balance(pk: int, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    repo = ProviderRepo(db)
    provider = repo.get_by_id(pk)
    if not provider:
        raise HTTPException(404, "Provider not found")
    key = repo.get_first_key(pk)
    if not key:
        raise HTTPException(404, "No active API key")
    api_key = repo.decrypt_key(key.id)
    if not api_key:
        raise HTTPException(400, "Cannot decrypt API key")
    adapter = ProviderRegistry.get(provider.name)
    if not adapter:
        raise HTTPException(400, "Unknown provider")
    result = await adapter.check_balance(
        provider.base_url, provider.api_path, api_key,
        balance_path=provider.balance_path,
    )
    return {"balance": result}


# ── Logs ───────────────────────────────────────────

@router.get("/logs")
def list_logs(skip: int = 0, limit: int = 50, provider_id: int = None,
              db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    rows, total = LogRepo(db).get_all(skip=skip, limit=limit, provider_id=provider_id)
    return {"total": total,
            "items": [{"id": r.id, "provider_id": r.provider_id, "model": r.model,
                       "request_body": r.request_body, "response_body": r.response_body,
                       "status_code": r.status_code, "tokens_used": r.tokens_used,
                       "latency_ms": r.latency_ms, "error_message": r.error_message,
                       "created_at": str(r.created_at)} for r in rows]}


@router.get("/logs/{pk}")
def get_log(pk: int, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    r = LogRepo(db).get_by_id(pk)
    if not r:
        raise HTTPException(404, "Log not found")
    return {"id": r.id, "provider_id": r.provider_id, "model": r.model,
            "request_body": r.request_body, "response_body": r.response_body,
            "status_code": r.status_code, "tokens_used": r.tokens_used,
            "latency_ms": r.latency_ms, "error_message": r.error_message,
            "created_at": str(r.created_at)}


# ── API Keys（代理 Key 管理）─────────────────────

class RouteCreateBody(BaseModel):
    alias: str
    provider_id: int
    api_key: str
    model: str = ""

class RouteUpdateBody(BaseModel):
    alias: str | None = None
    provider_id: int | None = None
    api_key: str | None = None
    model: str | None = None
    enabled: bool | None = None


@router.get("/routes")
def list_routes(db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    repo = RouteRepo(db)
    rows = repo.get_all()
    return [{"id": r.id, "alias": r.alias, "provider_id": r.provider_id,
             "model": r.model,
             "api_key": repo.decrypt_key(r.id),
             "enabled": r.enabled, "created_at": str(r.created_at)} for r in rows]


@router.post("/routes")
def create_route(body: RouteCreateBody, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    repo = RouteRepo(db)
    if repo.get_by_alias(body.alias):
        raise HTTPException(400, f"名称 '{body.alias}' 已存在")
    r = repo.create(alias=body.alias, provider_id=body.provider_id,
                    api_key=body.api_key, model=body.model)
    return {"id": r.id, "alias": r.alias, "provider_id": r.provider_id,
            "model": r.model, "enabled": r.enabled}


@router.put("/routes/{pk}")
def update_route(pk: int, body: RouteUpdateBody, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    repo = RouteRepo(db)
    r = repo.get_by_id(pk)
    if not r:
        raise HTTPException(404, "Route not found")
    data = body.model_dump(exclude_unset=True)
    if "api_key" in data and not data["api_key"]:
        del data["api_key"]
    if "alias" in data and data["alias"] != r.alias:
        if repo.get_by_alias(data["alias"]):
            raise HTTPException(400, f"名称 '{data['alias']}' 已存在")
    r = repo.update(pk, **data)
    return {"id": r.id, "alias": r.alias, "provider_id": r.provider_id,
            "model": r.model, "enabled": r.enabled}


@router.delete("/routes/{pk}")
def delete_route(pk: int, db: Session = Depends(get_db), _admin: str = Depends(require_admin)):
    repo = RouteRepo(db)
    if not repo.delete(pk):
        raise HTTPException(404, "Route not found")
    return {"ok": True}
