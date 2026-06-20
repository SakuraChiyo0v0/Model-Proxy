from app.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    name = "openai"
    label = "OpenAI"

    async def chat(self, request_body: dict, base_url: str, api_path: str, api_key: str) -> dict:
        import httpx
        url = base_url.rstrip("/") + api_path
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=120) as c:
            resp = await c.post(url, json=request_body, headers=headers)
        return resp.json()
