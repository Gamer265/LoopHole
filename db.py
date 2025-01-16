from motor.motor_asyncio import AsyncIOMotorClient

from config import Var
import sys

class DataBase:
    def __init__(self):
        try:
            print("Trying To Connect With MongoDB")
            self.client = AsyncIOMotorClient(Var.MONGO_SRV)
            self.channels = self.client["DBALP"]["channelWatchlist"]
            self.base_channel = self.client["DBALP"]["baseChannel"]
            print("Successfully Connected With MongoDB")
        except Exception as error:
            print(str(error))
            sys.exit(1)

    async def add_channel(self, chat_id, plus_views, time):
        await self.channels.update_one(
            {"_id": chat_id}, {"$set": {"surplus_views": plus_views, "interval": time}}, upsert=True
        )

    async def rem_channel(self, chat_id):
        data = await self.channels.find_one({"_id": chat_id})
        if data:
            await self.channels.delete_one({"_id": chat_id})

    async def get_channels(self):
        data = await self.channels.find()
        return (await data.to_list(length=None))

    async def is_channel_on_list(self, chat_id):
        data = await self.channels.find_one({"_id": chat_id})
        if data:
            return True, data.get("surplus_views"), data.get("interval")
        return False, None, None

    async def add_base_channel(self, chat_id):
        await self.base_channel.update_one(
            {"_id": "base"}, {"$set": {"chat_id": chat_id}}, upsert=True
        )

    async def get_base_channel(self):
        data = await self.base_channel.find_one({"_id": "base"})
        if data:
            return data.get("chat_id")
        return False

    