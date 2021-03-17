import sys
from typing import Optional

from vkbottle.bot import Blueprint

from models import User
from utils.rules import *
from utils.errors import WrongWarnsCountException
from utils.main import get_user_from_mention, give_warns

sys.path.append("..")
bp = Blueprint(name="Working with admin functions")


@bp.on.message_handler(OnlyAdminAccess(), AccessForBotAdmin(), text="бан", lower=True)
async def bot_ban_message(message: Message, _: Optional[User] = None):
    if message.reply_message:
        await message(
            f"ПОДТВЕРДИТЕ БАН ПОЛЬЗОВАТЕЛЯ С ID {message.reply_message.from_id}! НАПИШИТЕ 'ЗАБАНИТЬ' (ЗАГЛАВНЫМИ "
            f"БУКВАМИ) ДЛЯ ТОГО, ЧТОБЫ ЗАБАНИТЬ, ИЛИ 'ВЫЙТИ' (ЗАГЛАВНЫМИ), ЧТОБЫ ВЫЙТИ ИЗ ЭТОГО МЕНЮ! "
        )
        await BOT.branch.add(
            message.peer_id,
            "bot_ban_branch",
            user_id=message.reply_message.from_id,
            admin_id=message.from_id,
        )


@bp.branch.simple_branch("bot_ban_branch")
async def bot_ban_branch(message: Message, user_id, admin_id):
    returning = False
    if message.text == "ЗАБАНИТЬ" and message.from_id == admin_id:
        await BOT.api.request(
            "messages.removeChatUser", {"chat_id": message.chat_id, "user_id": user_id}
        )
        await message(
            f"Пользователь c ID {user_id} был забанен администратором с ID {admin_id}"
        )
        returning = True
        await BOT.branch.exit(message.peer_id)
    elif message.text == "ВЫЙТИ" and message.from_id == admin_id:
        await message("Был выполнен выход с меню бана")
        returning = True
        await BOT.branch.exit(message.peer_id)

    if message.from_id == admin_id and not returning:
        await message(
            f"ПОДТВЕРДИТЕ БАН ПОЛЬЗОВАТЕЛЯ С ID {user_id}! НАПИШИТЕ 'ЗАБАНИТЬ' (ЗАГЛАВНЫМИ БУКВАМИ) ДЛЯ ТОГО, ЧТОБЫ "
            f"ЗАБАНИТЬ, ИЛИ 'ВЫЙТИ' (ЗАГЛАВНЫМИ), ЧТОБЫ ВЫЙТИ ИЗ ЭТОГО МЕНЮ! "
        )


@bp.on.chat_message(OnlyAdminAccess(), text="/пред <mention> <count>", lower=True)
async def warn_with_mention_message(message: Message, _: Optional[User] = None, mention: str = None, count: str = None):
    mention = get_user_from_mention(mention)
    if not mention:
        await message("Упоминание обязательно")
        return None

    try:
        count = int(count)

        user = await User.get_or_none(user_id=mention, peer_id=message.peer_id)
        await give_warns(message, user, count)

    except ValueError:
        await message("Количество должно быть числом, что логично, но, видимо, нет. LoL")

    except WrongWarnsCountException:
        await message("Неверное количество выдаваемых варнов")


@bp.on.chat_message(OnlyAdminAccess(), text="/пред <count>", lower=True)
async def warn_with_reply_message(message: Message, _: Optional[User] = None, count: str = None):
    if not message.reply_message:
        await message("Отвеченное сообщение обязательно")
        return None

    try:
        count = int(count)

        user = await User.get_or_none(user_id=message.reply_message.from_id, peer_id=message.peer_id)
        await give_warns(message, user, count)

    except ValueError:
        await message("Количество должно быть числом, что логично, но, видимо, нет. LoL")

    except WrongWarnsCountException:
        await message("Неверное количество выдаваемых варнов")
