import asyncio
from pathlib import Path
from typing import Optional, Dict, List

import shortuuid
from backend.config import file_path1

MEMORY_PATH = file_path1.MEMORY_PATH

class SessionCreate:
    def __init__(self):
        self.session_id: str = ""
        self.conversation_file: Optional[Path] = None

    def _session_workspace(self, session_id: str) -> Path:
        return Path(MEMORY_PATH) / session_id

    def _conversation_file(self, session_id: str) -> Path:
        return self._session_workspace(session_id) / "conversation.jsonl"

    def _ensure_session(self, session_id: str) -> Path:
        """确保会话文件夹和文件存在"""
        folder = self._session_workspace(session_id)
        folder.mkdir(parents=True, exist_ok=True)
        conv_file = self._conversation_file(session_id)
        if not conv_file.exists():
            conv_file.touch()
        return conv_file

    def create(self) -> tuple:
        """创建新会话，返回 (session_id, conversation_file)"""
        session_id = shortuuid.uuid()[:8]
        conv_file = self._ensure_session(session_id)
        self.session_id = session_id
        self.conversation_file = conv_file
        return session_id, conv_file

    def get_or_create(self, session_id: str) -> Path:
        """获取或创建会话文件"""
        conv_file = self._ensure_session(session_id)
        self.session_id = session_id
        self.conversation_file = conv_file
        return conv_file

    def list_sessions(self) -> List[str]:
        """列出所有会话"""
        if not Path(MEMORY_PATH).exists():
            return []
        return [d.name for d in Path(MEMORY_PATH).iterdir() if d.is_dir()]

    def select_session(self, session_id: str) -> Path:
        """选择指定会话"""
        conv_file = self._ensure_session(session_id)
        self.session_id = session_id
        self.conversation_file = conv_file
        return conv_file


session_create = SessionCreate()