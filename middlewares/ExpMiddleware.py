from vkbottle import Message
from vkbottle.ext import Middleware

from config import NEW_START
from utils.consts import BOT
from models import Car, User, Conversation
from utils.main import check_or_create


@BOT.middleware.middleware_handler()
class ExpMiddleware(Middleware):
    async def pre(self, message: Message, *args):
        if not NEW_START:
            user = (await check_or_create(message.from_id, message.peer_id))[0]
            if not message.text.startswith("/"):
                if user.car_id is not None:
                    multiplier = (await Car.get(id=user.car_id)).multiplier
                else:
                    multiplier = 1

                msg = [a for a in message.text]
                msg = [a for a in msg if a != " "]
                exps = 2 * len(msg) * multiplier
                chat = await Conversation.get(peer_id=message.peer_id)
                await User.get(
                    user_id=message.from_id, chat=chat
                ).update(exp=exps + user.exp)
