import time
import uuid

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import AIMessage
from loguru import logger
_OFFLOAD_THRESHOLD = 1500
_OFFLOAD_DIR = "research_data"
_SUMMARY_LENGTH = 1500
class ToolResultOffloadMiddleware(AgentMiddleware):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend

    def _extract_tool_info(self, request):
        tool_name = None
        tool_args = None
        tool_call_id = ""
        start_time = time.time()

        if hasattr(request, 'messages'):
            messages = request.messages
            for message in reversed(messages):
                if not isinstance(message, AIMessage):
                    continue
                if not message.tool_calls:
                    continue
                tool_calls = message.tool_calls[0]
                tool_name = tool_calls.get("name")
                # tool_args = tool_calls.get("args", {})
                tool_call_id = tool_calls.get("id", uuid.uuid4().hex)

        elif isinstance(request, dict):
            tool_name = request.get("name")
            # tool_args = request.get("args", {})
            tool_call_id = request.get("id", uuid.uuid4().hex)

        return tool_name, tool_call_id

    def _get_ai_text(self, response):
        if hasattr(response, "result"):
            if response.result:
                text = response.result[0].content
                return text
        return None

    def _should_offload(self, tool_name, text):
        if not tool_name or not text:
            return False
        if len(text) < _OFFLOAD_THRESHOLD:
             return False
        return True

        # if tool_name in _RELAXED_OFFLOAD_TOOLS:
        #     return len(text) > _RELAXED_OFFLOAD_THRESHOLD
        # if tool_name in _OFFLOAD_TOOLS:
        #     return True
        # return len(text) > _OFFLOAD_THRESHOLD * 2

    def _make_file_path(self, tool_name):
        import uuid
        if tool_name:
            short_id = uuid.uuid4().hex[:8]
            safe_name = tool_name.replace("/", "_").replace(" ", "_")
        return f"{_OFFLOAD_DIR}/{safe_name}_{short_id}.md"

    def _make_summary(self, text: str, file_path: str) -> str:
        """Create a summary with file reference for the agent."""
        preview = text[:_SUMMARY_LENGTH]
        if len(text) > _SUMMARY_LENGTH:
            preview += "\n..."
        return (
            f"[Full result saved to {file_path} ({len(text)} chars). "
            f"Use read_file(\"{file_path}\") to access complete data. "
            f"NOTE: This file contains raw tool output. To use in sandbox scripts, "
            f"first read_file it, extract the data you need, then write_file a clean JSON file.]\n\n"
            f"{preview}"
        )

    def _offload_result(self, tool_name, tool_id, text):
        file_path = self._make_file_path(tool_name)
        try:
            self.backend.write(file_path, text)
            logger.info(
                f"[Offload] {tool_name} result ({len(text)} chars) → {file_path}"
            )
            summary = self._make_summary(text, file_path)
            return summary
        except Exception as exc:
            logger.warning(f"[Offload] Failed to write {file_path}: {exc}")
            return text

    def _replace_result_text(self, response, summary:str):
        if summary == "" :
            return response
        if hasattr(response, "result"):
            response.result[0].content = summary
            return response
        return response


    def wrap_model_call(self, request, handler):
        text:str = ""
        # print(request)
        response = handler(request)
        # print(response)

        tool_name, tool_id = self._extract_tool_info(request)
        text = self._get_ai_text(response)

        if self._should_offload(tool_name, text):
            summary = self._offload_result(tool_name, tool_id, text)
            return self._replace_result_text(response, summary)
        return response

