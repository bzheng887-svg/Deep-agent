import asyncio
import concurrent.futures
import json
import time
from typing import Any

import shortuuid
from langchain_core.messages import HumanMessage, AIMessage

from backend.deepagent.agent import deep_agent
from backend.deepagent.sse_middleware import SSEMonitoringMiddleware


class SessionStart:
    def __init__(self):
        self.agent = self._run_async_safe(deep_agent())
        self._sse_middleware: SSEMonitoringMiddleware = None
        # Find and store SSE middleware reference
        for m in getattr(self.agent, 'runtime_tools', []):
            if isinstance(m, SSEMonitoringMiddleware):
                self._sse_middleware = m
                break

    def _run_async_safe(self, coro):
        """安全地运行异步函数，无论是否在事件循环中"""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # 没有运行中的循环，直接运行
            return asyncio.run(coro)
        else:
            # 有运行中的循环，在新线程中运行
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()

    def get_sse_middleware(self) -> SSEMonitoringMiddleware:
        """Get the SSE monitoring middleware"""
        return self._sse_middleware

    def _load_message(self, file, content):
        messages = []
        newmess = []
        if not file.exists():
            return []

        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    messages.append(json.loads(line))

        for mes in messages:
            newmess.append({"role": mes.get("role"), "content": mes.get("content")})
        newmess.append({"role": "user", "content": content})
        # print(newmess)
        return newmess

    def send_message(self, file, content):
        res:dict["str": Any] = {}

        # message = HumanMessage(content)
        message = self._load_message(file, content)
        res = self.agent.invoke({"messages": message})

        if res:
            messages = res.get("messages")
            # print(messages[-1])


        return res.get("messages")[-1].content


session_start = SessionStart()
