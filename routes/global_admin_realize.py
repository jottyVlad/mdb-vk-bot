import random
import sys
from typing import Optional

from tortoise import Tortoise
from vkbottle.bot import Blueprint

from utils.consts import MAX_RANDOM_ID_INT, MIN_RANDOM_ID_INT
from global_settings import *
from models import Conversation, User, Work
from rules import *
from utils.main import is_mention

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
    conn = Tortoise.get_connection("default")
    # TODO: переименовать dct, магически цифры в константу
    # dct = await conn.execute_query_dict(
    #    "SELECT * FROM `users` WHERE `user_id` = 500101793"
    # )
    dct = await User.get(user_id=500101793)
    await message(dct)


# TODO: нужно ли?
@bp.on.message_handler(OnlyBotModerAccess(), text="/mention <mention>", lower=True)
async def mention_test(message: Message, _: Optional[User] = None, mention: str = None):
    print(mention.split("|")[0][1:])
    await message("[id{0}|Maxim]".format(message.from_id))


@bp.on.message_handler(OnlyBotModerAccess(), text="~ <text>", lower=True)
async def print_or_count(message: Message, _: Optional[User] = None, text: str = None):
    try:
        text = text.replace(" ", "")
        copied_text = text

        # TODO: в константу в config.py
        allowed_words = []
        allowed_words.extend([str(a) for a in range(10)])
        allowed_words.extend(
            [
                "sin",
                "sqrt",
                "+",
                "-",
                "j",
                "*",
                "/",
                "(",
                ")",
                "cos",
                "tan",
                "e",
                "pi",
                "ceil",
                "copysign",
                "fabs",
                "factorial",
                "floor",
                "fmod",
                "frexp",
                "ldexp",
                "fsum",
                "isfinite",
                "isinf",
                "isnan",
                "modf",
                "trunc",
                "exp",
                "expm1",
                "log",
                "log1p",
                "log10",
                "log2",
                "pow",
                "acos",
                "asin",
                "atan",
                "atan2",
                "hypot",
                "degrees",
                "radians",
                "cosh",
                "sinh",
                "tanh",
                "**",
                "acosh",
                "asinh",
                "atanh",
                "gamma",
                "lgamma",
            ]
        )
        awset = set(allowed_words)

        for i in awset:
            if i in copied_text:
                copied_text = copied_text.replace(i, "")

        if copied_text == "":
            all_good = True
        else:
            all_good = False

        if all_good:
            # TODO: тесты для проверки евала на безопасность !!!
            summ = eval(text)
            await message(summ)
        else:
            await message(text)

    except ZeroDivisionError:
        await message("+-inf")
    except Exception:
        await message(text)


# TODO: выделить хероту в отдельный метод, который принимает аргументом "роль"
@bp.on.message_handler(OnlyBotAdminAccess(), text="/снять_модер <mention>", lower=True)
async def delete_bot_moder(message: Message, mention: str, _: Optional[User] = None):
    if (is_mention(mention))[0]:
        mention = (is_mention(mention))[1]

    else:
        await message("Мне нужно упоминание человека, с которого снять модерку!")
        return

    global_role_default = await GlobalRole.get(name="Default")
    await GlobalUser.get(user_id=mention).update(
        global_role=global_role_default
    )
    await message("Модерка успешно снята!")


@bp.on.message_handler(OnlyBotAdminAccess(), text="/дать_модер <mention>", lower=True)
async def give_bot_moder(message: Message, mention: str, _: Optional[User] = None):
    if (is_mention(mention))[0]:
        mention = (is_mention(mention))[1]

    else:
        await message("Мне нужно упоминание человека, которому дать права модератора!")
        return

    global_role_moder = await GlobalRole.get(name="Moderator")
    await GlobalUser.get(user_id=mention).update(
        global_role=global_role_moder
    )
    await message("Права модератора успешно выданы!")


@bp.on.message_handler(OnlyMaximSend(), text="/дать_админ <mention>", lower=True)
async def give_bot_admin(message: Message, _: Optional[User] = None, mention: str = None):
    if (is_mention(mention))[0]:
        mention = (is_mention(mention))[1]

    else:
        await message("Мне нужно упоминание человека, которому дать права модератора!")
        return

    global_role_moder = await GlobalRole.get(name="Administrator")
    await GlobalUser.get(user_id=mention).update(
        global_role=global_role_moder
    )
    await message("Права администратора успешно выданы!")


@bp.on.message_handler(OnlyMaximSend(), text="/снять_админ <mention>", lower=True)
async def delete_bot_admin(message: Message, _: Optional[User] = None, mention: str = None):
    if (is_mention(mention))[0]:
        mention = (is_mention(mention))[1]

    else:
        await message("Мне нужно упоминание человека, с которого снять админку!")
        return

    global_role_default = await GlobalRole.get(name="Default")
    await GlobalUser.get(user_id=mention).update(
        global_role=global_role_default
    )
    await message("Админка успешно снята!")


# TODO: Выделить в метод два последних содержания
@bp.on.message_handler(OnlyMaximSend(), text="/бд добавить <model_name> <value>")
async def add_to_db(message: Message, _: Optional[User] = None, model_name: str = None, value: str = None):
    # TODO: нормальное приведение строки к словарю
    value = eval(value)
    if model_name == "GlobalRole":
        returnable = await GlobalRole(name=value["name"]).save()
    elif model_name == "GlobalUser":
        returnable = await GlobalUser(
            user_id=value["user_id"], global_role=value["global_role"]
        ).save()
    elif model_name == "User":
        returnable = await User(**value).save()
    elif model_name == "Conversation":
        returnable = await Conversation(**value).save()
    elif model_name == "Work":
        returnable = await Work(**value).save()
    elif model_name == "Car":
        returnable = await Car(**value).save()

    await message(str(returnable))


@bp.on.message_handler(OnlyMaximSend(), text="/бд удалить <model> <value>")
async def delete_from_db(message: Message, _: Optional[User] = None, model: str = None, value: str = None):
    try:
        # TODO: нормальное приведение строки к словарю
        value = eval(value)
        if model == "GlobalRole":
            await GlobalRole.get(name=value["name"]).delete()
        elif model == "GlobalUser":
            await GlobalUser.get(
                user_id=value["user_id"], global_role=value["global_role"]
            ).delete()
        elif model == "User":
            await User.get(**value).delete()
        elif model == "Conversation":
            await Conversation.get(**value).delete()
        elif model == "Work":
            await Work.get(**value).delete()
        elif model == "Car":
            await Car.get(**value).delete()

        await message("Удалено!")
    except Exception as _:
        await message("Ошибка удаления!")


# TODO: исправить метод
@bp.on.message_handler(OnlyBotModerAccess(), text="/доступ", lower=True)
async def access_message(message: Message, _: Optional[User] = None):
    global access_for_all  # ?
    access_for_all = not access_for_all
    with open("settings.json", "w") as write_file:
        ujson.dump({"access": access_for_all}, write_file)

    if access_for_all:
        await message("Доступ разрешен для всех")
    else:
        await message("Доступ разрешен только для администраторов")
