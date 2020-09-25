import sys
import random

from vkbottle.bot import Blueprint

from global_settings import *
from models import Conversation, User, GlobalUser, GlobalRole
from rules import *


sys.path.append("..")
bp = Blueprint(name="Working with actions functions")


@bp.on.chat_invite()
async def invite_message(action: Message):
    await BOT.api.request(
        "messages.send",
        {
            "message": 'Всем привет! Для того, чтобы я отвечал на сообщения, выдайте мне "Доступ ко всей переписке". Для доступа ко всем функциям выдайте мне права "Администратора"',
            "random_id": random.randint(-2e9, 2e9),
            "peer_id": action.peer_id,
        },
    )
    await Conversation(peer_id=action.peer_id).save()
