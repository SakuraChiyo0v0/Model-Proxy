import time
import json
import uuid

import httpx
from sqlalchemy.orm import Session

from app.repository.provider_repo import ProviderRepo
from app.repository.log_repo import LogRepo
from app.providers.registry import ProviderRegistry


class AuthService:

    @staticmethod
    def create_admin_token(db: Session) -> str:
        import uuid
        from app.repository.user_repo import UserRepo
        token = uuid.uuid4().hex
        user = UserRepo(db).get_by_username("admin")
        if user:
            user.token = token
            db.commit()
        return token

    @staticmethod
    def get_admin_token(db: Session) -> str | None:
        from app.repository.user_repo import UserRepo
        user = UserRepo(db).get_by_username("admin")
        return user.token if user else None

    @staticmethod
    def authenticate(db: Session, model: str) -> tuple[dict | None, str | None]:
        if not model:
            return None, "No 'model' field in request"
        repo = ProviderRepo(db)
        provider = repo.match_by_model(model)
        if not provider:
            return None, f"No provider matched model '{model}'"
        key = repo.get_first_key(provider.id)
        if not key:
            return None, f"Provider '{provider.name}' has no active API key"
        raw_key = repo.decrypt_key(key.id)
        return {
            "provider_id": provider.id,
            "provider_name": provider.name,
            "api_key": raw_key,
            "base_url": provider.base_url,
            "api_path": provider.api_path,
        }, None


class ProxyService:
    @staticmethod
    async def forward(request_body: dict, info: dict, db: Session) -> tuple[int, dict, str | None]:
        log_kwargs = {
            "provider_id": info["provider_id"],
            "model": request_body.get("model", ""),
            "request_body": json.dumps(request_body, ensure_ascii=False),
        }
        start = time.time()

        try:
            status, body, err = await ProxyService._do_request(request_body, info)
            elapsed = int((time.time() - start) * 1000)
            log_kwargs.update(status_code=status, latency_ms=elapsed,
                response_body=json.dumps(body, ensure_ascii=False) if body else err,
                error_message=err)
            if body and "usage" in body:
                log_kwargs["tokens_used"] = body.get("usage", {}).get("total_tokens", 0) or 0
            LogRepo(db).create(**log_kwargs)
            return status, body, err
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            log_kwargs.update(status_code=502, latency_ms=elapsed,
                response_body=str(e), error_message=str(e))
            LogRepo(db).create(**log_kwargs)
            return 502, {"error": str(e)}, str(e)

    @staticmethod
    async def _do_request(body: dict, info: dict):
        adapter = ProviderRegistry.get(info["provider_name"])
        if not adapter:
            url = info["base_url"].rstrip("/") + info["api_path"]
            async with httpx.AsyncClient(timeout=120) as c:
                resp = await c.post(url, json=body,
                    headers={"Authorization": f"Bearer {info['api_key']}", "Content-Type": "application/json"})
                try:
                    return resp.status_code, resp.json(), None
                except Exception:
                    return resp.status_code, {}, resp.text or f"HTTP {resp.status_code}"
        result = await adapter.chat(request_body=body, base_url=info["base_url"],
                                     api_key=info["api_key"], api_path=info["api_path"])
        return 200, result, None
