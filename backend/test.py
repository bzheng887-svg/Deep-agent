import asyncio
from pathlib import Path

from model import CreateModelRequest
from router.models import create_model, ApiResponse
from user.dependencies import User
from mongodb.db import db
async def lifespan():
    await db.connect()

    exc = CreateModelRequest(name = "zbw", base_url="https://api.longcat.chat/openai", api_key="ak_2lF5NM8Jf6Bi2k81za9sV3sy7BD2E", model_name="LongCat-Flash-Chat")
    # class User(BaseModel):
    #     id: str
    #     username: str
    #     role: str = "user"
    user = User(id = "001", username = "zbw")

    res = await create_model(exc, user)
    print(res)
    await asyncio.sleep(1)
    await db.close()


asyncio.run(lifespan())
_BASE_WORKSPACE = Path.cwd()
print(_BASE_WORKSPACE)


