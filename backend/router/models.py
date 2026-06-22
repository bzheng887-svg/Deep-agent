import asyncio
import time
import uuid
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import Field, BaseModel

from model import CreateModelRequest, ModelConfig
from user.dependencies import User
from mongodb.db import db

class ApiResponse(BaseModel):
    code: int = Field(default=0)
    msg: str = Field(default="ok")
    data: Any = Field(default=None)

async def verify_model_connection(provider: str, base_url: str | None, api_key: str | None, model_name: str):
    """
    Verify model availability by making a simple request.
    """
    logger.info(
        f"[verify_model] provider={provider}, model_name={model_name}, base_url={base_url}, has_api_key={bool(api_key)}")
    try:
        if not api_key:
            raise ValueError("API Key is required for verification")

        if provider == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            logger.info("[verify_model] Using ChatGoogleGenerativeAI for Gemini")
            chat = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                max_output_tokens=5,
                timeout=10,
            )
        else:
            logger.info(f"[verify_model] Using ChatOpenAI, base_url={base_url or '(default)'}")
            chat = ChatOpenAI(
                model=model_name,
                api_key=api_key,
                base_url=base_url if base_url else None,
                max_tokens=5,
                timeout=10,
            )

        logger.info("[verify_model] Sending test message...")
        re = await chat.ainvoke([HumanMessage(content="Hi")])
        print(re)
        logger.info("[verify_model] Verification succeeded")
    except Exception as e:
        logger.error(f"[verify_model] Verification failed: {type(e).__name__}: {e}")



async def create_model(body: CreateModelRequest, current_user: User):
    """Add a user defined model"""
    logger.info(f"[create_model] provider={body.provider}, model_name={body.model_name}, "
                f"name={body.name}, base_url={body.base_url}, has_api_key={bool(body.api_key)}")

    await verify_model_connection(body.provider, body.base_url, body.api_key, body.model_name)

    model_id = str(uuid.uuid4())
    now = int(time.time())

    new_model = ModelConfig(
        id=model_id,
        name=body.name,
        provider=body.provider,
        base_url=body.base_url,
        api_key=body.api_key,
        model_name=body.model_name,
        context_window=body.context_window,
        is_system=False,
        user_id=current_user.id,
        is_active=True,
        created_at=now,
        updated_at=now
    )

    doc = new_model.model_dump()
    doc["_id"] = doc.pop("id")

    await db.get_collection("models").insert_one(doc)

    # Return with id
    return ApiResponse(data=new_model.model_dump())




# class CreateModelRequest(BaseModel):
#     name: str
#     provider: str = "openai"
#     base_url: Optional[str] = None
#     api_key: Optional[str] = None
#     model_name: str
#     context_window: Optional[int] = Field(
#         default=None,
#         ge=1024, le=10_000_000,
#         description="Model context window in tokens. Leave empty for auto-detection.",
#     )
