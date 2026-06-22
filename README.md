# DeepClaw

AI Agent 应用，前端 Vue 3，后端 Python FastAPI + LangChain。

## 项目结构

```
deepclaw/
├── backend/                    # FastAPI + LangChain Agent 系统
│   ├── main.py               # API 入口（CORS、会话、Chat SSE）
│   ├── config.py             # 环境配置（模型、API Key、路径）
│   ├── model.py              # ModelConfig Pydantic 模型
│   ├── deepagent/            # 核心 Agent 实现
│   │   ├── agent.py          # Agent 构建器（中间件、后端、工具加载）
│   │   ├── engine.py         # LLM 模型工厂（ChatOpenAI）
│   │   ├── sse_middleware.py # SSE 事件监控中间件
│   │   ├── offloadmiddleware.py # 大型工具结果卸载到文件
│   │   ├── full_backend.py   # 带策略校验的后端包装器
│   │   ├── sse_protocol.py   # 工具元数据注册表（图标、分类）
│   │   ├── session.py        # 会话管理
│   │   ├── message_middleware.py
│   │   ├── builtin_tools.py
│   │   └── dir_watcher.py    # 文件变更热重载检测
│   ├── builtin-skills/       # 内置 Skill 定义
│   │   ├── skill-creator/    # Skill 创建工作流 + 评估系统
│   │   └── tool-creator/     # Tool 创建工作流
│   ├── router/               # API 路由
│   │   ├── models.py         # 模型 CRUD + verify_model_connection()
│   │   └── session.py        # 会话创建
│   ├── session/              # 会话模块
│   │   ├── session_id_create.py
│   │   └── session_start.py
│   ├── mongodb/              # 数据库层（Motor 异步 MongoDB）
│   │   └── db.py
│   └── user/
│       └── dependencies.py
├── frontend/deepclaw/         # Vue 3 + Vite + TypeScript
│   └── src/
│       ├── App.vue           # 根组件
│       ├── main.ts
│       ├── api.ts            # API 调用封装
│       ├── config.ts
│       └── components/
├── tools/                    # 外部工具（动态加载）
│   └── tool_runner.py        # 工具调用器
├── skills/                   # 用户自定义 Skills
└── workspace/               # Agent 工作目录
```

## 核心架构

### Agent 系统

DeepAgent 采用分层中间件架构：
1. **ToolResultOffloadMiddleware** - 将大型工具结果写入 `research_data/`，返回摘要
2. **SSEMonitoringMiddleware** - 发送 SSE 事件（工具开始/完成）

**后端包装**: `PolicyWrapper` 包装 `LocalShellBackend`，包含策略检查（如禁止目录）。

### 工具加载

`tools/*.py` 中的外部工具通过 AST 解析加载。带有 `@tool` 装饰器（来自 `langchain_core.tools`）的函数注册为 `StructuredTool` 实例。目录变更时自动热重载。

### Skill 系统

Skill 是 `/builtin-skills/` 或 `/skills/` 下的指令文档（SKILL.md）。两个内置 Skill：
- `skill-creator` — 创建/修改 Skills，运行评估，迭代质量
- `tool-creator` — 创建 `@tool` 函数（遵循 snake_case 命名、类型提示、docstring、logging 模式）

### SSE 流式

工具执行事件通过 SSE 协议流式推送（见 `sse_middleware.py`）。

### Web 工具

使用 `seekr_sdk`（`from seekr_sdk import web_search, web_crawl`）进行网页搜索/爬取，**不要**使用原始 `httpx`。

## 环境配置

在 `backend/` 目录创建 `.env` 文件：

```env
DC_API_KEY=<your-api-key>
DC_MODEL=deepseek-chat
DC_URL=https://api.deepseek.com/v1
MAX_TOKENS=100000
CONTEXT_WINDOW=131072
```

## 启动

### 前端

```sh
cd frontend/deepclaw
npm install
npm run dev
```

### 后端

```sh
cd backend
# 启动 API 服务器
python -m uvicorn main:app --reload --port 8000

# 测试模型连接
python test.py
```

## 目录路径（config.py）

| 变量 | 路径 |
|------|------|
| `ROOT_DIR` | `D:\.deepclaw\` |
| `WORKSPACE_DIR` | `D:\.deepclaw\workspace\` |
| `EXT_SKILLS_DIR` | `~/.deepclaw/skills/` |
| `EXT_TOOLS_DIR` | `~/.deepclaw/tools/` |
| `MEMORY_DIR` | `~/.deepclaw/memory/` |
| `BUILTIN_SKILLS_DIR` | `backend/builtin-skills/` |

## API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| `POST` | `/api/chat` | 发送消息，SSE 流式返回 |
| `POST` | `/api/sessions` | 创建新会话 |
| `GET` | `/api/sessions` | 列出所有会话 |
| `GET` | `/api/sessions/{id}` | 获取指定会话 |
| `GET` | `/api/skills` | 列出所有 Skills |
| `POST` | `/api/skills` | 添加 Skill |
| `GET` | `/api/tools` | 列出所有 Tools |
| `POST` | `/api/tools` | 添加 Tool |

## 技术栈

- **前端**: Vue 3, Vite, TypeScript, axios
- **后端**: FastAPI, LangChain, Motor (MongoDB 异步驱动)
- **模型**: ChatOpenAI-compatible API (DeepSeek 默认)
