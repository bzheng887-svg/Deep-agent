import json
import time
import uuid
from typing import Any, Callable

from deepagents.backends import LocalShellBackend
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import SystemMessagePromptTemplate, PromptTemplate
from loguru import logger
from backend.deepagent.engine import get_llm_model
from deepagents import create_deep_agent
from langchain_core.tools import tool

from backend.deepagent.sse_protocol import get_protocol_meta

class SSEEvent:
    def __init__(self, event, data):
        self.event:str = event
        self.data:dict[str,Any] = data

    def to_dict(self):
        return {"event": self.event, "data": self.data}

class SSEMonitoringMiddleware(AgentMiddleware):
    """    工具执行前（_before_tool）：提取工具名称、参数，记录开始时间，发送SSE事件
        工具执行后（_after_tool）：计算耗时，提取结果摘要，发送SSE事件
        日志记录：输出工具开始 / 完成的日志（含图标和耗时）"""
    def __init__(self):
        super().__init__()
        self.sse_events:list[SSEEvent] = []

    def _before_tool(self, request: ModelRequest):
        tool_name = None
        tool_args = None
        tool_call_id = ""
        start_time = time.time()
        # print(request)
        if hasattr(request, 'messages'):
            messages = request.messages
            for message in reversed(messages):
                if not isinstance(message, AIMessage):
                    continue
                if not message.tool_calls:
                    continue
                tool_calls = message.tool_calls[0]
                tool_name = tool_calls.get("name")
                tool_args = tool_calls.get("args", {})
                tool_call_id = tool_calls.get("id", uuid.uuid4().hex)

        elif isinstance(request, dict):
            tool_name = request.get("name")
            tool_args = request.get("args", {})
            tool_call_id = request.get("id", uuid.uuid4().hex)

        tool_meta = get_protocol_meta(tool_name)

        if tool_name:
            self.sse_events.append(SSEEvent(event = "Middleware_before_tool", data={
                "tool_name": tool_name,
                "tool_args": tool_args,
                "tool_call_id": tool_call_id,
                "tool_meta": tool_meta,
                "start_time": start_time,
            }))

        # tool_calls_log

        logger.info(
            f"[{tool_name}] TOOL START: "
            f"{tool_meta.get('icon', '🔧')} {tool_name} | "
            f"args={json.dumps(tool_args or {}, ensure_ascii=False)[:200]}"
        )
        return tool_name, tool_args, tool_call_id, start_time, tool_meta

    def _after_tool(self, tool_name, tool_args, tool_call_id, start_time, tool_meta, response: ModelResponse):
        duration_ms = int((time.time() - start_time) * 1000)

        if tool_name:
            """处理response"""
            result_summary : str = ""

            try:
                res = response.result
                for r in res:
                    if not isinstance(r, AIMessage):
                        continue
                    result_summary = r.content

            except Exception as e:
                result_summary = "(error extracting result)"

            self.sse_events.append(SSEEvent(event="Middleware_after_tool", data={
                "tool_call_id": tool_call_id,
                "function": tool_name,
                "duration_ms": duration_ms,
                "tool_meta": tool_meta,
                "result_summary": result_summary,
                "timestamp": time.time(),
            }))

            logger.info(
                f"[{tool_name}] TOOL COMPLETE: "
                f"{tool_meta.get('icon', '🔧')} {tool_name} | "
                f"duration={duration_ms}ms"
            )
        return response

    def wrap_model_call(self, request: Any, handler: Callable):
        # 1. request: 这里我们读取并修改输入数据

        tool_name, tool_args, tool_call_id, start_time, tool_meta = self._before_tool(request)

        # 假设我们需要确保最后一条消息是用户的，并追加安全提示
        print(f"原始消息数: {len(request.messages)}")
        # if len(request.messages) > 2:
        #     print(request.messages[-2].content , "tool_calls->", request.messages[-2].tool_calls)
        #     print(request.messages[-1].content)

        # 2. handler: 将修改后的 request 传递给下一步 (即调用真正的 LLM)
        # handler(request) 会执行底层的 LLM 推理
        response = handler(request)

        # SessionStart._message_save(response.result[0])

        # print(response)

        response = self._after_tool(tool_name, tool_args, tool_call_id, start_time, tool_meta, response)

        # 3. 返回最终的 response
        return response



@tool
def get_wer(flag):
    """
    description:
        查询天气
    Args:
        flag=ture表示进行查询
    Returns:
        str = ""
    """
    return "今天天气37°"
system_template = PromptTemplate.from_template(
    "你是一个{role}"
)
def deep_agent():
    tools:list = [get_wer]
    model = get_llm_model()
    backend = LocalShellBackend(
        root_dir="D:\\deepclaw\\backend\\deepagent",
        virtual_mode=True,
        env={"PATH": "D:\\tools\\anaconda\\envs\\ml-backend"}  # 示例 Windows PATH 配置
    )
    system_prompt = system_template.format(role = "boy")
    agent = create_deep_agent(
        model,
        tools=tools,
        middleware=[],
        system_prompt=system_prompt,
        # backend=backend,
        # interrupt_on={
        #     "edit_file": True,
        #     "write_file": True,
        #     "execute": True  # 强烈建议对 LocalShellBackend 的执行操作启用此项
        # }
    )
    res = agent.invoke(input = {"messages":[HumanMessage(content="你什么性别")]})
    # print(res)

if __name__ == "__main__":
    deep_agent()