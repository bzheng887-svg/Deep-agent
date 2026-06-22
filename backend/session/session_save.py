import datetime
import json
import time

import pytz
import shortuuid
from langchain_core.messages import AIMessage, HumanMessage

from backend.session.session_id_create import session_create

beijing_tz = pytz.timezone("Asia/Shanghai")

# 转换为 ISO 8601 字符串格式


class SessionSave:



    def message_save(self, messages:AIMessage|HumanMessage):
        role = ""
        content = ""
        new_messages = []
        total_tokens = ""
        if isinstance(messages, HumanMessage):
            role = "user"
            content = messages.content

        if isinstance(messages, AIMessage):
            role = "assistant"
            content = messages.content
            total_tokens = messages.usage_metadata["total_tokens"]


        message = {
            "id": shortuuid.uuid()[:8],
            "role": role,  # "user" 或 "assistant"
            "content": content,
            "total_tokens": total_tokens,
            "timestamp": datetime.datetime.now(beijing_tz).isoformat(),
        }
        # if metadata:
        #     message["metadata"] = metadata
        # 写回文件
        with open(session_create.conversation_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(message, ensure_ascii=False) + "\n")

session_save = SessionSave()