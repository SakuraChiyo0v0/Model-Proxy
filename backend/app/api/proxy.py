import json
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.proxy_service import AuthService, ProxyService
from app.repository.route_repo import RouteRepo
from app.repository.provider_repo import ProviderRepo

router = APIRouter()


@router.post("/v1/chat/completions")
@router.post("/chat/completions")
async def chat_completions(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON body")

    # 1) 先检查是否是代理级 API Key（自定义 Key → 绑定厂商）
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        raw_key = auth_header[7:]
        route = RouteRepo(db).match_by_api_key(raw_key)
        if route:
            # 用路由绑定的模型覆盖请求体中的 model
            if route.model:
                body["model"] = route.model
            provider = ProviderRepo(db).get_by_id(route.provider_id)
            if not provider or not provider.enabled:
                raise HTTPException(502, "绑定厂商不可用")
            key = ProviderRepo(db).get_first_key(provider.id)
            if not key:
                raise HTTPException(502, "绑定厂商无可用 Key")
            info = {
                "provider_id": provider.id,
                "provider_name": provider.name,
                "api_key": ProviderRepo(db).decrypt_key(key.id),
                "base_url": provider.base_url,
                "api_path": provider.api_path,
            }
            status, result, _ = await ProxyService.forward(body, info, db)
            if status != 200:
                raise HTTPException(status, detail=result.get("error", result))
            return result

    # 2) 回退：按 model 字段匹配厂商
    model = body.get("model", "")
    info, error = AuthService.authenticate(db, model)
    if error:
        raise HTTPException(401, error)

    status, result, _ = await ProxyService.forward(body, info, db)
    if status != 200:
        raise HTTPException(status, detail=result.get("error", result))
    return result
