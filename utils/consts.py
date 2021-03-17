import asyncio
from enum import Enum

from vkbottle import Bot, User as vkBottleUser

from config import ACCESS_TOKEN, BOT_GROUP_ID, USER_ACCESS_TOKEN

MAX_RANDOM_ID_INT = int(2e9)
MIN_RANDOM_ID_INT = int(-2e9)
START_WRITE_POSITION_X = 30
START_WRITE_POSITION_Y = 50
BLACK_COLOR = (0, 0, 0)
BOT_CREATOR_ID = 500101793

CAR_COST_MULTIPLIER = 0.1


class DatabaseActions(Enum):
    ADD = 0
    REMOVE = 1


class AccessingLevels(Enum):
    MODERATOR = "Модерка"
    ADMINISTRATOR = "Администраторка"


class BuyCarUserStatuses(Enum):
    APPROVED = 0
    NOT_ENOUGH_MONEY = 1
    NOT_ENOUGH_EXP = 2
    NOW_HAVE_CAR = 3


BOT = Bot(ACCESS_TOKEN, loop=asyncio.get_event_loop(), group_id=BOT_GROUP_ID)
USER = vkBottleUser(USER_ACCESS_TOKEN)