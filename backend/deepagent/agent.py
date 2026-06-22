import asyncio
from datetime import datetime, timedelta
import os
import threading
from typing import Optional, Dict, Any, Tuple, List

from deepagents import create_deep_agent, MemoryMiddleware
from deepagents.backends import LocalShellBackend, FilesystemBackend, CompositeBackend
from deepagents.middleware import SkillsMiddleware
from deepagents.middleware.subagents import DEFAULT_SUBAGENT_PROMPT, GENERAL_PURPOSE_SUBAGENT
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from loguru import logger
from backend.deepagent.message_middleware import MessageMiddleware
from backend.config import file_path1
from backend.deepagent.builtin_tools import propose_skill_save, web_search
from backend.deepagent.full_backend import PolicyWrapper
from backend.deepagent.engine import get_llm_model
from backend.deepagent.dir_watcher import watcher as _dir_watcher
from backend.deepagent.sse_middleware import SSEMonitoringMiddleware
from backend.tools import reload_external_tools, tool_runner
from backend.deepagent.offloadmiddleware import ToolResultOffloadMiddleware
EXT_SKILLS_DIR = str(file_path1.EXT_SKILLS_DIR)
EXT_TOOLS_DIR = str(file_path1.EXT_TOOLS_DIR)
BUILTIN_SKILLS_DIR = str(file_path1.BUILTIN_SKILLS_DIR)
MEMORY_DIR = file_path1.MEMORY_DIR
WORKSPACE_DIR = str(file_path1.WORKSPACE_DIR)
ROOT_DIR = str(file_path1.ROOT_DIR)
PYTHON_DIR = file_path1.PYTHON_DIR
ENV_DIR = file_path1.ENV_DIR


# _STATIC_TOOLS = [
#     web_search, web_crawl, propose_skill_save, propose_tool_save,
#     eval_skill, grade_eval,
#     tooluniverse_search, tooluniverse_info, tooluniverse_run,
# ]
_STATIC_TOOLS = [
    propose_skill_save, web_search
]

def _collect_tools():
    all_tools: List = []
    ext_tools: List = []
    try:
        ext_tools = reload_external_tools(EXT_TOOLS_DIR)

    except Exception:
        logger.warning("[Agent] 动态加载外部工具失败", exc_info=True)

    all_tools = ext_tools + _STATIC_TOOLS

    logger.info(f"[Agent] 自定义工具列表({len(all_tools)}): {[t.name for t in all_tools]}")
    return all_tools

def _build_backend(window_backend):
    """
    CompositeBackend->{
      - /builtin-skills/ 路由: FilesystemBackend（内置 skills）
      - /skills/          路由: FilesystemBackend（外置 skills）
      - /tools/             路由: FilesystemBackend（外置 tools）
    """
    routes = {}

    if os.path.isdir(BUILTIN_SKILLS_DIR):
        logger.info(f"[Skills] 内置 skills: {BUILTIN_SKILLS_DIR} → /builtin-skills/")

        routes["/builtin-skills/"] = FilesystemBackend(
            root_dir=BUILTIN_SKILLS_DIR,
            virtual_mode=True,
        )

    if os.path.isdir(EXT_SKILLS_DIR):
        logger.info(f"[Skills] 外置 skills: {EXT_SKILLS_DIR} → /skills/")
        routes["/skills/"] = FilesystemBackend(
            root_dir=EXT_SKILLS_DIR,
            virtual_mode=True,
        )

    if os.path.isdir(EXT_TOOLS_DIR):
        logger.info(f"[tools] 外置 tools: {EXT_TOOLS_DIR} → /tools/")
        routes["/tools/"] = FilesystemBackend(
            root_dir=EXT_TOOLS_DIR,
            virtual_mode=True,
        )

    if os.path.isdir(MEMORY_DIR):
        logger.info(f"[MEMORY] 外置 全局MEMORY: {MEMORY_DIR} → /memory/")
        routes["/memory/"] = FilesystemBackend(
            root_dir=MEMORY_DIR,
            virtual_mode=True,
        )

    # if os.path.isdir(PYTHON_DIR):
    #     logger.info(f"[PYTHON] 外置 PYTHON: {PYTHON_DIR} → /pythonenv/")
    #     routes["/python_env/"] = FilesystemBackend(
    #         root_dir=PYTHON_DIR,
    #         virtual_mode=True,
    #     )
    #
    # if os.path.isdir(ENV_DIR):
    #     logger.info(f"[ENV] 外置 ENV: {ENV_DIR} → /env/")
    #     routes["/env/"] = FilesystemBackend(
    #         root_dir=ENV_DIR,
    #         virtual_mode=True,
    #     )


    if routes:
        # 返回工厂函数以确保路由生效
        backend = CompositeBackend(default=window_backend, routes=routes)
        return backend
    else:
        return window_backend

_SYSTEM_PROMPT = PromptTemplate(
    template = """你是DeepClaw，一个积极主动的个人AI助手，旨在帮助用户高效地解决问题、进行研究并完成任务。
    
当前日期和时间：{current_datetime}。

## 语言
请始终用{language_instruction}进行回复。

## 核心原则
- 适应对话。对于非正式的话题，可以自然地聊天，但当用户询问任务或寻求解决问题时，要采取实际行动。
- 执行优于解释。如果一项任务可以通过代码或工具来解决，那么就实施并执行解决方案，而不仅仅是描述它。
- **实时信息**：对于任何涉及当前或最新信息的问题，你必须使用`web_search` — 绝不能仅凭训练数据来回答。
- **写入文件，而非聊天内容**：当用户要求编写、创建或生成代码/脚本/文件时，务必使用`write_file`来创建真实的文件——而绝非仅在聊天中粘贴代码。
- **编写→执行→修复循环**：在编写任何可执行脚本后，必须立即通过`execute`运行它以验证其正确性。如果运行失败，则进行修复并重新运行。
- **技能优先原则**：在开始任何任务之前，务必检查可用的技能（`/builtin-skills/` 和 `/skills/`）。如果找到匹配的技能，则`读取`其 SKILL.md 文件并遵循工作流程。切勿重复开发技能已提供的功能。
- **SKILL.md文件是指导文档** — 使用`read_file`来读取它们，切勿将其作为脚本`execute`。
- 主动解决问题。只有在意图或要求确实不明确时，才提出问题。

## 工作区
您的工作区目录为{workspace_dir}/。
- 所有文件都应使用绝对路径在此目录下创建。
- 工作区由文件系统和执行沙箱共享。

## 任务完成策略
### 步骤1：理解与规划
- 确定所有可交付成果、要求和输出格式。
- 对于任何涉及2个以上步骤的任务，请在开始之前调用`write_todos`。
- 检查内存：**memory.md** 和 **CONTEXT.md**。
- **检查可用技能（必选）** — 查看技能目录。如果任何技能与任务匹配，则`读取`该SKILL.md文件并遵循其工作流程。请勿跳过此步骤。

### 步骤2：执行
- 如果某项技能匹配 → 完全遵循该技能的工作流程。
- 否则，直接使用工具。优先级：现有技能 > 内置工具 > ToolUniverse > 网络搜索。
- **在`propose_tool_save`之前**：请先阅读`/builtin-skills/tool-creator/SKILL.md`。
- **在调用 `propose_skill_save` 之前**：请先阅读 `/builtin-skills/skill-creator/SKILL.md`。
- 增量构建 — 每次工具调用构建一个组件。编写后通过`execute`进行测试。

### 步骤 3：验证与交付
- 重新阅读用户的原始请求。检查是否已生成所有可交付成果。
- 如果脚本失败，请修复具体错误，不要从头开始重写。如果失败次数超过2次，请简化脚本。

### 步骤4：反思与记录
在完成了一项非琐碎的任务之后：
- **可重复使用的工作流程** → 建议通过技能创建器将其保存为**技能**。
- **可重用函数** → 建议通过工具创建器将其保存为**工具**。
- **已获取用户偏好** → 通过`edit_file`更新**/memory/memory.md**。
- **了解项目背景** → 通过`edit_file`更新**CONTEXT.md**。

""",
    input_variables = ["current_datetime", "language_instruction", "workspace_dir"]
)

def get_system_prompt(lang_code: str):
    _LANGUAGE_DICT = {
        "zn" : ("Chinese (Simplified)", "你必须用简体中文来回答提出的问题，给出解决方案、撰写文档，文件夹和文件名字无特殊要求应为英文。"),
        "en" : ("English", "You must respond in English. All generated reports, document titles and body text must also be in English.")
    }
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lang_name, lang_detail = _LANGUAGE_DICT.get(lang_code, "Always respond in the same language the user uses.")
    language_instruction = f"""
    - The user has set their preferred language to **{lang_name}** (code: `{lang_code}`).\n
    - lang_detail: **{lang_detail}**.\n
    - This applies to ALL outputs: conversation replies, report content, section titles, chart labels.
    """
    system_prompt = _SYSTEM_PROMPT.format(current_datetime=now, language_instruction=language_instruction, workspace_dir=str(file_path1.WORKSPACE_DIR))
    return system_prompt

async def deep_agent():

    """   创建一个完整的 DeepAgent 实例（会话级隔离），并注入 SSE 监控中间件。

    Returns:
        (agent, sse_middleware, context_window, diagnostic_logger)

    Skills 架构：
      - 内置 skills（/builtin_skills/）：COPY 进镜像，始终加载
      - 外置 skills（/Skills/）：用户自管理，支持屏蔽过滤"""

    model = get_llm_model()

    context_window = getattr(model, "profile", {}).get("max_input_tokens", 131_072)

    print("context_window", context_window)

    # 外部skills加载
    _dir_watcher.has_changed(EXT_SKILLS_DIR)

    # 外部与内置tools加载
    tools = _collect_tools()

    # 工具记录中间件保存在 sse_middleware.sse_events
    sse_middleware = SSEMonitoringMiddleware()
    message_middleware = MessageMiddleware()
    # 后端物理地址:WORKSPACE_DIR
    # 后端逻辑:LocalShellBackend
    # 环境:"D:\\tools\\anaconda\\envs\\ml-backend"
    # 功能: 无
    window_backend = LocalShellBackend(
        root_dir=WORKSPACE_DIR,
        virtual_mode=True,
        env={"PATH": "C:\\Users\\10347\\.deepclaw\\python_env"}  )

    # 路由地址:/builtin-skills/、/skills/、/tools/
    # 物理地址:BUILTIN_SKILLS_DIR、EXT_SKILLS_DIR、EXT_TOOLS_DIR
    # 后端逻辑:FilesystemBackend
    backend = _build_backend(window_backend)
    # 约束输出中间件
    offload_middleware = ToolResultOffloadMiddleware(window_backend)

    agent_kwargs: Dict[str, Any] = {
        "model": model,
        "tools": tools,
        "middleware": [offload_middleware, sse_middleware, message_middleware],
    }

    system_prompt = get_system_prompt("zn")

    agent_kwargs["system_prompt"] = system_prompt
    agent_kwargs["backend"] = backend

    # 填充skills
    skills_sources: List[str] = []
    if os.path.isdir(BUILTIN_SKILLS_DIR):
        skills_sources.append("/builtin-skills/")
    if os.path.isdir(EXT_SKILLS_DIR):
        skills_sources.append("/skills/")

    if skills_sources:
        agent_kwargs["skills"] = skills_sources
        logger.info(f"[Agent] 已启用 Skills（sources: {skills_sources}")


    memory_dir = MEMORY_DIR
    os.makedirs(memory_dir, exist_ok=True)
    memory_md = os.path.join(memory_dir, "memory.md")

    if not os.path.isfile(memory_md):
        with open(memory_md, "w", encoding="utf-8") as f:
            f.write("# Global Memory\n\n"
                    "## User Preferences\n\n"
                    "## General Patterns\n\n"
                    "## Notes\n")
        logger.info(f"[Memory] 初始化全局 Memory: {memory_md}")

    context_dir = os.path.join(ROOT_DIR, "workspace")
    os.makedirs(context_dir, exist_ok=True)
    context_md = os.path.join(context_dir, "CONTEXT.md")

    if not os.path.isfile(context_md):
        with open(context_md, "w", encoding="utf-8") as f:
            f.write("# Session Context (this session only)\n\n"
                    "## Project Context\n\n"
                    "## Task Notes\n")
        logger.info(f"[Memory] 初始化会话 Context: {context_md}")

    _MAX_MEMORY_CHARS = 4000
    _mem_files_to_use = []
    # for _mf in [memory_md, context_md]:
    #     try:
    #         _mf_size = os.path.getsize(_mf)
    #         if _mf_size > _MAX_MEMORY_CHARS:
    #             with open(_mf, "r", encoding="utf-8") as f:
    #                 _full = f.read()
    #             _truncated = _full[:_MAX_MEMORY_CHARS].rsplit("\n", 1)[0]
    #             _tmp_path = _mf + ".truncated"
    #             with open(_tmp_path, "w", encoding="utf-8") as f:
    #                 f.write(_truncated + "\n\n(Memory truncated — keep entries concise to stay under limit)\n")
    #             _mem_files_to_use.append(_tmp_path)
    #             logger.warning(
    #                 f"[Memory] {os.path.basename(_mf)} too large ({_mf_size:,} chars), "
    #                 f"truncated to {_MAX_MEMORY_CHARS:,} for injection"
    #             )
    #         else:
    #             _mem_files_to_use.append(_mf)
    #     except Exception:
    #         _mem_files_to_use.append(_mf)

    agent_kwargs["memory"] = ["/memory/memory.md", context_md]
    # logger.info(f"[Memory] 已启用记忆: {[os.path.basename(f) for f in _mem_files_to_use]}")

    _subagent_policy = f"""\n
    ### 工作空间
    你的工作空间目录是 {WORKSPACE_DIR}\。
    所有文件都应在此目录下使用绝对路径创建。
    SKILL.md 文件是说明文档——使用 `read_file` 来读取它们，绝不要 `execute`。
    
    ## Skills CLI（关键）
    绝不要使用 `npx skills`。直接使用 `skills`。安装时：`HOME={WORKSPACE_DIR} skills add <package> -g -y --agent '*'`。所有标志都是必须的——省略任何一个都会在交互提示时挂起。
    
    """
    GENERAL_PURPOSE_SUBAGENT["system_prompt"] = DEFAULT_SUBAGENT_PROMPT + _subagent_policy

    agent = create_deep_agent(**agent_kwargs)

    GENERAL_PURPOSE_SUBAGENT["system_prompt"] = DEFAULT_SUBAGENT_PROMPT

    return agent
if __name__ == "__main__":
    # print(ROOT_DIR)

    agent = asyncio.run(deep_agent())
    while True:
        qur = input(">")
        res = agent.invoke({"messages":[HumanMessage(content=qur)]})
        print(res)