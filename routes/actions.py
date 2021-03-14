import random
import sys
from typing import Optional

from vkbottle.bot import Blueprint

from config import MIN_RANDOM_ID_INT, MAX_RANDOM_ID_INT
from global_settings import *
from models import Conversation, User
from rules import *

sys.path.append("..")
bp = Blueprint(name="Working with actions functions")


@bp.on.chat_invite()
async def invite_message(action: Message, _: Optional[User] = None):
    await BOT.api.request(
        "messages.send",
        {
            "message": 'Всем привет! Для того, чтобы я отвечал на сообщения, выдайте мне "Доступ ко всей переписке". '
                       'Для доступа ко всем функциям выдайте мне права "Администратора"',
            "random_id": random.randint(MIN_RANDOM_ID_INT, MAX_RANDOM_ID_INT),
            "peer_id": action.peer_id,
        },
    )
    await Conversation(peer_id=action.peer_id).save()
