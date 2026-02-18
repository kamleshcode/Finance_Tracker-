import os

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_URL")

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
            self.db = self.client["finance_db"]
            await self.create_indexes()
            print("Connected to MongoDB")
        except Exception as e:
            print("Failed to connect to MongoDB :",e)

    def close(self):
        try:
            self.client.close()
        except Exception as e:
            print("Failed to close MongoDB :",e)

    async def create_indexes(self):
        try:
            tx = self.db.transactions
            cat = self.db.categories
            await tx.create_index([("date", -1)])
            await tx.create_index([("category", 1), ("date", -1)])
            await tx.create_index([("type", 1), ("date", -1)])
            await tx.create_index([("title", "text"), ("description", "text")])
            await cat.create_index("name", unique=True)

            print("Indexes Created")
        except Exception as e:
            print("Failed to create indexes :",e)

mongodb = MongoDB()
