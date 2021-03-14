import asyncio

from vkbottle import User as vkBottleUser, Bot

from config import ACCESS_TOKEN, USER_ACCESS_TOKEN
from utils.main import get_access_for_all

BOT = Bot(ACCESS_TOKEN, loop=asyncio.get_event_loop(), group_id=196816306)
USER = vkBottleUser(USER_ACCESS_TOKEN)

#TODO: создать utils.py и переместить туда функции

access_for_all = asyncio.get_event_loop().run_until_complete(get_access_for_all())


