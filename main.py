# backend/main.py

import asyncio
import json
import time
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.config import file_path1
from backend.session.session_id_create import session_create

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class Message(BaseModel):
    text: str
    session_id: Optional[str] = None

class SkillInfo(BaseModel):
    name: str
    path: str
    description: str = ""

class ToolInfo(BaseModel):
    name: str
    path: str
    description: str = ""

# --- Session Management ---
@app.post("/api/sessions")
async def create_session():
    """创建新会话"""
    session_id, conversation_file = session_create.create()
    return {"session_id": session_id}

@app.get("/api/sessions")
async def list_sessions():
    """列出所有会话"""
    sessions = session_create.list_sessions()
    return {"sessions": sessions}

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """获取指定会话"""
    conv_file = session_create.get_or_create(session_id)
    return {"session_id": session_id, "conversation_file": str(conv_file)}

# --- Chat with SSE ---
@app.post("/api/chat")
async def chat(msg: Message):
    """发送消息并流式返回"""
    if not msg.session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    # 获取或创建会话文件
    conversation_file = session_create.get_or_create(msg.session_id)

    async def event_stream():
        try:
            # 懒加载，避免启动时阻塞
            from backend.session.session_start import session_start

            # 发送用户消息
            yield f"data: {json.dumps({'event': 'user_message', 'data': {'content': msg.text, 'timestamp': int(time.time())}}, ensure_ascii=False)}\n\n"

            # 获取AI响应
            response = session_start.send_message(conversation_file, msg.text)

            # 发送AI回复
            yield f"data: {json.dumps({'event': 'assistant_message', 'data': {'content': response, 'timestamp': int(time.time())}}, ensure_ascii=False)}\n\n"

            # 发送工具事件
            sse_middleware = session_start.get_sse_middleware()
            if sse_middleware:
                for evt in sse_middleware.sse_events:
                    yield f"data: {json.dumps(evt.to_dict(), ensure_ascii=False)}\n\n"
                sse_middleware.sse_events.clear()

            yield "data: {\"event\": \"done\", \"data\": {}}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'data': {'message': str(e)}}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

# --- Skills ---
@app.get("/api/skills")
async def list_skills():
    skills = []
    builtin_dir = Path(file_path1.BUILTIN_SKILLS_DIR)
    ext_skills_dir = Path(file_path1.EXT_SKILLS_DIR)

    for skill_dir in (builtin_dir if builtin_dir.exists() else Path()).iterdir():
        if skill_dir.is_dir():
            skill_md = skill_dir / "SKILL.md"
            desc = ""
            if skill_md.exists():
                content = skill_md.read_text(encoding="utf-8")
                if "---" in content:
                    for line in content.split("---")[1].split("\n"):
                        if line.startswith("description:"):
                            desc = line.replace("description:", "").strip().strip('"')
                            break
            skills.append(SkillInfo(name=skill_dir.name, path=str(skill_dir), description=desc))

    if ext_skills_dir.exists():
        for skill_dir in ext_skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                desc = ""
                if skill_md.exists():
                    content = skill_md.read_text(encoding="utf-8")
                    if "---" in content:
                        for line in content.split("---")[1].split("\n"):
                            if line.startswith("description:"):
                                desc = line.replace("description:", "").strip().strip('"')
                                break
                skills.append(SkillInfo(name=skill_dir.name, path=str(skill_dir), description=desc))

    return {"skills": skills}

@app.post("/api/skills")
async def add_skill(skill: SkillInfo):
    try:
        import shutil
        source = Path(skill.path)
        if not source.exists():
            raise HTTPException(status_code=400, detail="Invalid path")
        dest = Path(file_path1.EXT_SKILLS_DIR) / source.name
        shutil.copytree(source, dest, dirs_exist_ok=True)
        return {"message": "Skill added"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Tools ---
@app.get("/api/tools")
async def list_tools():
    tools = []
    ext_tools_dir = Path(file_path1.EXT_TOOLS_DIR)
    if ext_tools_dir.exists():
        for py_file in ext_tools_dir.glob("*.py"):
            if py_file.name.startswith("_") or py_file.name == "__init__.py":
                continue
            content = py_file.read_text(encoding="utf-8")
            desc = f"Tool: {py_file.stem}"
            if '"""' in content:
                start = content.index('"""') + 3
                end = content.index('"""', start)
                desc = content[start:end].strip().split("\n")[0]
            tools.append(ToolInfo(name=py_file.stem, path=str(py_file), description=desc))
    return {"tools": tools}

@app.post("/api/tools")
async def add_tool(tool: ToolInfo):
    try:
        import shutil
        source = Path(tool.path)
        if not source.exists():
            raise HTTPException(status_code=400, detail="Invalid path")
        dest = Path(file_path1.EXT_TOOLS_DIR) / source.name
        shutil.copy(source, dest)
        return {"message": "Tool added"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Basic ---
@app.post("/send")
async def send(msg: Message):
    return {"message": f"收到: {msg.text}"}

@app.get("/")
def root():
    return {"message": "Hello FastAPI"}