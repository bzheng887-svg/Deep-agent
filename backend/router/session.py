from typing import Optional, Any

from pydantic import BaseModel, Field
from user.dependencies import User

class CreateSessionRequest(BaseModel):
    mode: str = Field(default="deep", description="Session mode")
    model_config_id: Optional[str] = Field(default=None, description="Model config ID")

class ApiResponse(BaseModel):
    code: int = Field(default=0, description="Business status code, 0 means success")
    msg: str = Field(default="ok", description="Business message")
    data: Any = Field(default=None, description="Response data")

async def create_session(
    current_user: User, body: CreateSessionRequest = CreateSessionRequest()
) -> ApiResponse:
    try:
        model_config_dict = None
        if body.model_config_id:
            mc = await get_model_config(body.model_config_id)
            if mc:
                if not mc.is_system and mc.user_id != current_user.id:
                    raise Exception("Cannot use this model")
                model_config_dict = mc.model_dump()

        session = await async_create_science_session(
            mode=body.mode,
            user_id=current_user.id,
            model_config=model_config_dict,
        )
        return ApiResponse(data=CreateSessionData(session_id=session.session_id, mode=session.mode).model_dump())
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("create_session failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc