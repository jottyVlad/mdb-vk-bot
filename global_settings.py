import asyncio

from vkbottle import User as vkBottleUser, Bot

from config import ACCESS_TOKEN, USER_ACCESS_TOKEN, BOT_GROUP_ID
from utils.main import get_access_for_all

BOT = Bot(ACCESS_TOKEN, loop=asyncio.get_event_loop(), group_id=BOT_GROUP_ID)
USER = vkBottleUser(USER_ACCESS_TOKEN)

access_for_all = asyncio.get_event_loop().run_until_complete(get_access_for_all())
