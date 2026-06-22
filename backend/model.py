import time
import uuid
from pydantic import BaseModel, Field
from typing import Optional, List
from mongodb.db import db
class ModelConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Display Name")
    provider: str = Field(..., description="openai, anthropic, etc.")
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: str = Field(..., description="Actual model name e.g. gpt-4o")
    context_window: Optional[int] = Field(
        default=None,
        description="Model context window in tokens. Auto-detected from model_name if not set.",
    )
    is_system: bool = False
    user_id: Optional[str] = None
    is_active: bool = True
    created_at: int = Field(default_factory=lambda: int(time.time()))
    updated_at: int = Field(default_factory=lambda: int(time.time()))

class CreateModelRequest(BaseModel):
    name: str
    provider: str = "openai"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: str
    context_window: Optional[int] = Field(
        default=None,
        ge=1024, le=10_000_000,
        description="Model context window in tokens. Leave empty for auto-detection.",
    )

async def get_model_config(model_id: str) -> Optional[ModelConfig]:
    doc = await db.get_collection("models").find_one({"_id": model_id})
    if not doc:
        return None
    # Remap _id to id
    doc["id"] = doc["_id"]
    return ModelConfig(**doc)