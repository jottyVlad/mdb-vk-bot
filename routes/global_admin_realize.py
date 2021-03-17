import random
import sys
from typing import Optional

import numexpr as ne
import ujson
from vkbottle.bot import Blueprint

from models import Conversation, User
from utils.rules import *
from utils.consts import MAX_RANDOM_ID_INT, MIN_RANDOM_ID_INT, DatabaseActions, BOT_CREATOR_ID, AccessingLevels
from utils.db_methods import add_or_remove_model, give_or_take_access
from utils.errors import DatabaseDeleteException, DatabaseAddException, ParseMentionException

sys.path.append("..")
bp = Blueprint(name="Working with global admin functions")


@bp.on.message_handler(OnlyBotAdminAccess(), text="/разослать <text>", lower=True)
async def send_messages(message: Message, _: Optional[User] = None, text: str = None):
    await BOT.api.request(
        "messages.markAsRead",
        {"peer_id": message.peer_id, "mark_conversation_as_read": "1"},
    )
    convs = await Conversation.all().values_list("peer_id", flat=True)
    if convs:
        for conv in convs:
            await BOT.api.messages.send(
                peer_id=conv, random_id=random.randint(MIN_RANDOM_ID_INT, MAX_RANDOM_ID_INT), message=text
            )

    await message("Выполнено.")


@bp.on.message_handler(OnlyMaximSend(), text="/получить_себя")
async def get_myself(message: Message, _: Optional[User] = None):
    user = str(await User.get(user_id=BOT_CREATOR_ID))
    await message(user)


# NOTE: нужно ли?
@bp.on.message_handler(OnlyBotModerAccess(), text="/mention <mention>", lower=True)
async def mention_test(message: Message, _: Optional[User] = None, mention: str = None):
    # print(mention.split("|")[0][1:])
    await message("[id{0}|Maxim]".format(message.from_id))


@bp.on.message_handler(OnlyBotModerAccess(), text="~ <text>", lower=True)
async def print_or_count(message: Message, _: Optional[User] = None, text: str = None):
    try:
        summ = ne.evaluate(text).item()
        await message(summ)

    except ZeroDivisionError:
        await message("Делить на 0 нельзя!")
    except Exception:
        await message(text)


@bp.on.message_handler(OnlyBotAdminAccess(), text="/снять_модер <mention>", lower=True)
async def delete_bot_moder(message: Message, mention: str, _: Optional[User] = None):
    try:
        result = await give_or_take_access(AccessingLevels.MODERATOR, DatabaseActions.REMOVE, mention)
    except ParseMentionException:
        await message("Мне нужно упоминание человека, с которого снять модерку!")
    else:
        await message(result)


@bp.on.message_handler(OnlyBotAdminAccess(), text="/дать_модер <mention>", lower=True)
async def give_bot_moder(message: Message, mention: str, _: Optional[User] = None):
    try:
        result = await give_or_take_access(AccessingLevels.MODERATOR, DatabaseActions.ADD, mention)
    except ParseMentionException:
        await message("Мне нужно упоминание человека, которому дать модерку!")
    else:
        await message(result)


@bp.on.message_handler(OnlyMaximSend(), text="/дать_админ <mention>", lower=True)
async def give_bot_admin(message: Message, _: Optional[User] = None, mention: str = None):
    try:
        result = await give_or_take_access(AccessingLevels.ADMINISTRATOR, DatabaseActions.ADD, mention)
    except ParseMentionException:
        await message("Мне нужно упоминание человека, которому дать админку")
    else:
        await message(result)


@bp.on.message_handler(OnlyMaximSend(), text="/снять_админ <mention>", lower=True)
async def delete_bot_admin(message: Message, _: Optional[User] = None, mention: str = None):
    try:
        result = await give_or_take_access(AccessingLevels.ADMINISTRATOR, DatabaseActions.REMOVE, mention)
    except ParseMentionException:
        await message("Мне нужно упоминание человека, с которого снять админку!")
    else:
        await message(result)


@bp.on.message_handler(OnlyMaximSend(), text="/бд добавить <model_name> <value>")
async def add_to_db(message: Message, _: Optional[User] = None, model_name: str = None, value: str = None):
    try:
        result = await add_or_remove_model(model_name, value, DatabaseActions.ADD)
    except DatabaseAddException:
        await message("Нет такой таблицы!")
    else:
        await message(result)


@bp.on.message_handler(OnlyMaximSend(), text="/бд удалить <model_name> <value>")
async def delete_from_db(message: Message, _: Optional[User] = None, model_name: str = None, value: str = None):
    try:
        result = await add_or_remove_model(model_name, value, DatabaseActions.REMOVE)
    except DatabaseDeleteException:
        await message("Ошибка удаления!")
    else:
        await message(result)


@bp.on.message_handler(OnlyBotModerAccess(), text="/доступ", lower=True)
async def access_message(message: Message, _: Optional[User] = None):
    access_for_all: bool = await get_access_for_all()
    access_for_all = not access_for_all
    with open("../settings.json", "w") as write_file:
        ujson.dump({"access": access_for_all}, write_file)

    if access_for_all:
        await message("Доступ разрешен для всех")
    else:
        await message("Доступ разрешен только для администраторов")
