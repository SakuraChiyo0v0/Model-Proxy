PROVIDER_TEMPLATES = [
    # OpenAI — 官方新支持 /v1/balances 余额查询
    {
        "name": "openai",
        "label": "OpenAI",
        "base_url": "https://api.openai.com",
        "api_path": "/v1/chat/completions",
        "auth_type": "bearer",
        "models_path": "/v1/models",              # 官方：GET /v1/models
        "balance_path": "/v1/balances",           # 官方：GET /v1/balances（2025新增）
    },
    # DeepSeek — 余额/模型路径非标准 OpenAI
    {
        "name": "deepseek",
        "label": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "api_path": "/v1/chat/completions",
        "auth_type": "bearer",
        "models_path": "/models",                 # 官方：GET /models
        "balance_path": "/user/balance",          # 官方：GET /user/balance
    },
    # 火山引擎 豆包（方舟 Ark）— 无标准 OpenAI 模型列表 API
    {
        "name": "doubao",
        "label": "豆包（火山方舟）",
        "base_url": "https://ark.cn-beijing.volces.com",
        "api_path": "/api/v3/chat/completions",
        "auth_type": "bearer",
        "models_path": None,                      # Ark 无标准 /v1/models，需用 ListEndpoints API
        "balance_path": None,                     # 仅在火山引擎控制台查看
    },
    # Anthropic Claude — 非 OpenAI 协议（x-api-key 认证），代理需特殊处理
    {
        "name": "claude",
        "label": "Claude（Anthropic）",
        "base_url": "https://api.anthropic.com",
        "api_path": "/v1/messages",
        "auth_type": "x-api-key",                 # 用 x-api-key 头而非 Bearer，需加 anthropic-version 头
        "models_path": "/v1/models",              # 官方：GET /v1/models（需 x-api-key 认证）
        "balance_path": None,                     # 不支持 API 查余额
    },
    # 阿里云 通义千问（百炼 DashScope OpenAI兼容模式）
    {
        "name": "qwen",
        "label": "通义千问（阿里云百炼）",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode",
        "api_path": "/v1/chat/completions",
        "auth_type": "bearer",
        "models_path": "/v1/models",              # OpenAI 兼容：GET /compatible-mode/v1/models
        "balance_path": None,                     # 通过阿里云百炼控制台查询余额
    },
    # 智谱 AI（BigModel）— OpenAI 兼容
    {
        "name": "zhipu",
        "label": "智谱AI（GLM）",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_path": "/chat/completions",
        "auth_type": "bearer",
        "models_path": "/models",                 # OpenAI 兼容：GET /api/paas/v4/models
        "balance_path": None,                     # 通过智谱开放平台控制台查看
    },
    # Moonshot（Kimi 开放平台）— 官方文档确认支持余额 API
    {
        "name": "moonshot",
        "label": "Moonshot（Kimi）",
        "base_url": "https://api.moonshot.cn",
        "api_path": "/v1/chat/completions",
        "auth_type": "bearer",
        "models_path": "/v1/models",              # 官方：GET /v1/models
        "balance_path": "/v1/users/me/balance",   # 官方：GET /v1/users/me/balance
    },
    # MiniMax — 官方 API 地址为 api.minimaxi.com
    {
        "name": "minimax",
        "label": "MiniMax（稀宇科技）",
        "base_url": "https://api.minimaxi.com",
        "api_path": "/v1/chat/completions",
        "auth_type": "bearer",
        "models_path": "/v1/models",              # 官方：GET /v1/models
        "balance_path": None,                     # 控制台查看
    },
    # 百川智能 — 兼容 OpenAI 协议
    {
        "name": "baichuan",
        "label": "百川智能",
        "base_url": "https://api.baichuan-ai.com",
        "api_path": "/v1/chat/completions",
        "auth_type": "bearer",
        "models_path": "/v1/models",              # OpenAI 兼容：GET /v1/models
        "balance_path": None,                     # 控制台查看
    },
    # xAI Grok — 官方文档确认 /v1/models 和 /v1/language-models
    {
        "name": "xai",
        "label": "xAI Grok",
        "base_url": "https://api.x.ai",
        "api_path": "/v1/chat/completions",
        "auth_type": "bearer",
        "models_path": "/v1/models",              # 官方：GET /v1/models
        "balance_path": None,                     # 无余额查询 API，通过 console.x.ai 查看
    },
    # Ollama 本地部署
    {
        "name": "ollama",
        "label": "Ollama（本地部署）",
        "base_url": "http://localhost:11434",
        "api_path": "/v1/chat/completions",
        "auth_type": "bearer",                    # Ollama 默认不需要认证，格式兼容
        "models_path": "/api/tags",               # Ollama 非标准：GET /api/tags
        "balance_path": None,                     # 本地部署无余额概念
    },
]
