import asyncio

from loguru import logger
from pymongo import AsyncMongoClient
from motor.motor_asyncio import AsyncIOMotorClient
class MongoDB:
    client = None
    db = None

    @classmethod
    async def connect(cls):
        try:
            if cls.client is None:
                uri = "mongodb://localhost:27017/"
                cls.client = AsyncMongoClient(uri)
                cls.db = cls.client["example_collection"]

                await cls.client.admin.command("ping")
                logger.info("Successfully connected to MongoDB")
                await cls.init_indexes()
        except Exception as e:
            raise Exception(
                "The following error occurred: ", e)

    @classmethod
    async def close(cls):
        if cls.client:
            await cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("MongoDB connection closed")

    @classmethod
    async def init_indexes(cls):
        """Create necessary indexes"""
        if cls.db is None:
            return
        await cls.db.users.create_index(
            "username",
            unique=True
        )

        # sessions
        await cls.db.sessions.create_index("user_id")

        await cls.db.sessions.create_index(
            [("updated_at", -1)]
        )

        # session_events
        await cls.db.session_events.create_index(
            "session_id"
        )

        await cls.db.session_events.create_index(
            [("timestamp", 1)]
        )

        # blocked_skills
        await cls.db.blocked_skills.create_index(
            [("user_id", 1), ("skill_name", 1)],
            unique=True
        )

        # TTL
        await cls.db.im_message_dedup.create_index(
            "created_at",
            expireAfterSeconds=86400
        )

    @classmethod
    def get_collection(cls, collection_name: str):
        if cls.db is None:
            # Lazy connect or raise error.
            # Ideally connection should be established at startup.
            raise RuntimeError("Database not initialized. Call connect() first.")
        return cls.db[collection_name]


db = MongoDB


# async def main():
#     try:
#         # start example code here
#         uri = "mongodb://localhost:27017/"
#         client = AsyncMongoClient(uri)
#         # end example code here
#         database = client["test_database"]
#         await database.create_collection("example_collection")
#         await client.admin.command("ping")
#         print("Connected successfully")
#
#         # other application code
#
#         await client.close()
#
#     except Exception as e:
#         raise Exception(
#             "The following error occurred: ", e)



# asyncio.run(db.connect())