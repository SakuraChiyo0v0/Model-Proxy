from app.providers.base import BaseProvider


class DeepSeekProvider(BaseProvider):
    name = "deepseek"
    label = "DeepSeek"

    async def chat(self, request_body: dict, base_url: str, api_path: str, api_key: str) -> dict:
        import httpx
        url = base_url.rstrip("/") + api_path
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=120) as c:
            resp = await c.post(url, json=request_body, headers=headers)
        return resp.json()

    async def check_balance(self, base_url: str, api_path: str, api_key: str,
                            balance_path: str | None = None) -> dict | None:
        if not balance_path:
            return None
        import httpx
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                resp = await c.get(f"{base_url.rstrip('/')}{balance_path}",
                    headers={"Authorization": f"Bearer {api_key}"})
            data = resp.json()
            if resp.status_code == 200 and "balance_infos" in data:
                info = data["balance_infos"][0]
                return {
                    "total_balance": info.get("total_balance"),
                    "total_used": info.get("total_used"),
                    "currency": info.get("currency", "CNY"),
                }
            return None
        except Exception:
            return None

    # list_models 使用基类实现（通过 models_path 参数）
