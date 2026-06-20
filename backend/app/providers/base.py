from abc import ABC, abstractmethod
from typing import Optional


class BaseProvider(ABC):
    name: str = ""
    label: str = ""

    @abstractmethod
    async def chat(self, request_body: dict, base_url: str, api_path: str, api_key: str) -> dict:
        ...

    async def test_connectivity(self, base_url: str, api_path: str, api_key: str) -> tuple[bool, str]:
        """测试连通性：先尝试 models 接口，失败则发最小 chat 请求"""
        import httpx
        headers = {"Authorization": f"Bearer {api_key}"}
        async with httpx.AsyncClient(timeout=10) as c:
            # 方案1：尝试 models 接口（轻量，不需要 model 参数）
            models_url = base_url.rstrip("/") + "/v1/models"
            try:
                r = await c.get(models_url, headers=headers)
                if r.status_code == 200:
                    return True, "连接成功"
                if r.status_code == 401 or r.status_code == 403:
                    return False, f"API Key 无效 ({r.status_code})"
            except Exception:
                pass
            # 方案2：尝试 /models（DeepSeek 等非标准路径）
            try:
                r = await c.get(base_url.rstrip("/") + "/models", headers=headers)
                if r.status_code == 200:
                    return True, "连接成功"
                if r.status_code == 401 or r.status_code == 403:
                    return False, f"API Key 无效 ({r.status_code})"
            except Exception:
                pass
            # 方案3：发 chat 请求（兜底）
            url = base_url.rstrip("/") + api_path
            headers["Content-Type"] = "application/json"
            body = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1}
            try:
                resp = await c.post(url, json=body, headers=headers)
                if resp.status_code == 200:
                    return True, "连接成功"
                if resp.status_code == 401 or resp.status_code == 403:
                    return False, f"API Key 无效 ({resp.status_code})"
                if 400 <= resp.status_code < 500:
                    return True, f"Key 有效 (服务器已响应, HTTP {resp.status_code})"
                return False, f"连接失败: HTTP {resp.status_code}"
            except Exception as e:
                return False, str(e)

    async def check_balance(self, base_url: str, api_path: str, api_key: str,
                            balance_path: str | None = None) -> Optional[dict]:
        """查询余额。balance_path 为 None 表示不支持，返回 None。
        子类可重写以处理特定响应格式。"""
        if not balance_path:
            return None
        import httpx
        try:
            url = base_url.rstrip("/") + balance_path
            async with httpx.AsyncClient(timeout=10) as c:
                resp = await c.get(url, headers={"Authorization": f"Bearer {api_key}"})
            if resp.status_code == 200:
                data = resp.json()
                # 尝试适配常见余额响应格式
                # 格式1：{total_available, total_used, ...}  (OpenAI, Moonshot)
                if "total_available" in data or "total_available_usd" in data:
                    return {
                        "total_balance": data.get("total_granted_usd") or data.get("total_balance"),
                        "total_used": data.get("total_used_usd") or data.get("total_used"),
                        "currency": "USD",
                    }
                # 格式2：{balance_infos: [{total_balance, ...}]}  (DeepSeek)
                if "balance_infos" in data:
                    info = data["balance_infos"][0]
                    return {
                        "total_balance": info.get("total_balance"),
                        "total_used": info.get("total_used"),
                        "currency": info.get("currency", "CNY"),
                    }
                # 格式3：{data: {balance, ...}}  (Moonshot 兼容)
                if "data" in data and isinstance(data["data"], dict):
                    d = data["data"]
                    if "balance" in d or "total_balance" in d:
                        return {
                            "total_balance": str(d.get("total_balance") or d.get("balance", "")),
                            "total_used": str(d.get("total_used", "")),
                            "currency": d.get("currency", "CNY"),
                        }
                # 未知格式，原样返回
                return {"raw": data}
            return None
        except Exception:
            return None

    async def list_models(self, base_url: str, api_path: str, api_key: str,
                          models_path: str | None = None) -> list[str]:
        """获取模型列表。models_path 为 None 表示不支持"""
        if not models_path:
            return []
        import httpx
        url = base_url.rstrip("/") + models_path
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                resp = await c.get(url, headers={"Authorization": f"Bearer {api_key}"})
            if resp.status_code == 200:
                data = resp.json()
                models = []
                for m in data.get("data", []):
                    mid = m.get("id", "")
                    if mid and not any(skip in mid for skip in
                                       ("dall-e", "tts", "whisper", "embedding",
                                        "moderation", "babbage", "davinci",
                                        "speech", "audio")):
                        models.append(mid)
                return models
        except Exception:
            pass
        return []


class DefaultProvider(BaseProvider):
    """默认适配器，用于未注册专用适配器的厂商"""
    name = "default"
    label = "Default"

    async def chat(self, request_body: dict, base_url: str, api_path: str, api_key: str) -> dict:
        raise NotImplementedError("Default provider should not be used for chat.")
