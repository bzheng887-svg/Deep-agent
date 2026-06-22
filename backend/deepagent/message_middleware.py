from typing import Any, Callable

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import AIMessage, HumanMessage
from backend.session.session_save import session_save

class MessageMiddleware(AgentMiddleware):

    def __init__(self):
        super().__init__()

    def wrap_model_call(self, request: Any, handler: Callable):

        # print(request)

        if isinstance(request.messages[-1], HumanMessage):
            session_save.message_save(request.messages[-1])

        # print(request.messages)
        response = handler(request)
        if isinstance(response.result[0], AIMessage):
            session_save.message_save(response.result[0])
            print(response)

        return response