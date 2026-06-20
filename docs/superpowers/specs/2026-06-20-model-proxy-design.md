# Model Proxy - 设计文档

**日期**: 2026-06-20
**目标**: 构建一个统一 AI 模型代理网关，整合多厂商 API，提供 Web 管理后台 + 兼容 OpenAI 的 API 接口

---

## 1. 核心功能

- **API 统一接入**：以插件式架构接入 OpenAI、DeepSeek、豆包等多厂商模型
- **Key 前缀路由**：通过 API Key 前缀（如 `sk-doubao`）自动路由到对应厂商
- **请求日志**：记录每个请求的完整链路信息，便于追踪和调试
- **Web 管理后台**：管理 Key 配置、厂商设置、查看日志

## 2. 架构设计

```
┌───────────────┐    ┌──────────────────────────────────────┐
│  React 管理后台 │━━━→│            FastAPI 后端               │
└───────────────┘    │  ┌──────┐ ┌──────────┐ ┌──────────┐  │
                     │  │ API层│→│Service层 │→│Provider层│  │
    调用方 ─────────→│  └──────┘ └────┬─────┘ └──────────┘  │
                     │                │                      │
                     │           ┌────▼────┐                │
                     │           │  DB 层   │                │
                     │           │ SQLite  │                │
                     │           └─────────┘                │
                     └──────────────────────────────────────┘
```

- **API 层**：路由定义、请求验证、JWT 鉴权
- **Service 层**：Key 前缀解析、Provider 调度、加密/解密、日志记录
- **Provider 层**：各厂商 API 适配器，统一转为 OpenAI 格式
- **DB 层**：SQLAlchemy + SQLite

## 3. 数据库设计

| 表 | 说明 | 核心字段 |
|---|------|---------|
| providers | 厂商配置 | name, base_url, api_path, enabled |
| api_keys | API Key | key_prefix(唯一), key_value(AES加密), provider_id |
| request_logs | 请求日志 | model, request/response_body, tokens, latency_ms |
| users | 管理用户 | username, password_hash |

## 4. API 设计

- `/v1/chat/completions` — 兼容 OpenAI 格式的代理接口（Bearer Token 鉴权）
- `/api/admin/*` — 管理后台 API（JWT 鉴权）

## 5. Provider 插件设计

- `BaseProvider` 抽象基类，定义 `chat()` 方法
- `ProviderRegistry` 全局注册表
- 新增厂商：继承 BaseProvider + 数据库添加记录

## 6. 安全设计

- API Key 使用 AES-256-CBC 可逆加密存储于 SQLite
- 加密密钥通过环境变量注入
- 管理后台 JWT 鉴权
- Key 前缀匹配路由，精确到厂商

## 7. 技术栈

- 后端：Python 3.11+ / FastAPI / SQLAlchemy / SQLite
- 前端：React 18+ / Vite / TailwindCSS（OpenAI 风格 UI）
