from enum import Enum

MAX_RANDOM_ID_INT = int(2e9)
MIN_RANDOM_ID_INT = int(-2e9)
START_WRITE_POSITION_X = 30
START_WRITE_POSITION_Y = 50
BLACK_COLOR = (0, 0, 0)
BOT_CREATOR_ID = 500101793


class DatabaseActions(Enum):
    ADD = 0
    REMOVE = 1


class AccessingLevels(Enum):
    MODERATOR = "Модерка"
    ADMINISTRATOR = "Администраторка"
