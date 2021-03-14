import os
import sys
from typing import Optional

import aiohttp
import ujson
from vkbottle.bot import Blueprint

from global_settings import *
from models import User
from rules import *
from utils.db_methods import check_or_create
from utils.main import make_profile_photo, send_with_bomb, create_poll, is_replied_self

sys.path.append("..")
bp = Blueprint(name="Working with users functions")


@bp.on.message_handler(AccessForAllRule(), text="привет", lower=True)
async def hi_message(ans: Message, _: Optional[User] = None):
    await ans("Привет, чувачелла")


@bp.on.message_handler(AccessForAllRule(), text="максим", lower=True)
async def maxim_message(ans: Message, _: Optional[User] = None):
    await send_with_bomb("Максим админ тут да ага бота создаватель в беседе повеливатель ага да м-да...", ans.peer_id)


@bp.on.message_handler(AccessForAllRule(), text="мда", lower=True)
async def mda_message(ans: Message, _: Optional[User] = None):
    await send_with_bomb("Да мда конечно это такое мда что прямо м-да...", ans.peer_id)


@bp.on.message_handler(AccessForAllRule(), text=["/профиль", "/profile"], lower=True)
async def profile_message(message: Message, profile: Optional[User] = None):
    if message.reply_message \
            and ((message.from_id != message.reply_message)
                 and (message.from_id not in ADMINS_IN_CONV)):
        await message("Доступ запрещен!")
        return

    upload_srv = (await BOT.api.photos.get_messages_upload_server()).upload_url

    await make_profile_photo(profile)
    files = {'photo': open(f"{profile.user_id}.jpeg", "rb")}
    async with aiohttp.ClientSession() as session:
        async with session.post(upload_srv, data=files) as resp:
            data = await resp.read()
            ready_json = ujson.loads(data)

    photo_object = await BOT.api.photos.save_messages_photo(
        server=ready_json["server"],
        photo=ready_json["photo"],
        hash=ready_json["hash"])

    os.remove(f"{profile.user_id}.jpeg")
    await message(attachment=f"photo{photo_object[0].owner_id}_{photo_object[0].id}")


@bp.on.message_handler(AccessForAllRule(), text=["/помощь", "/help"], lower=True)
async def help_message(message: Message, _: Optional[User] = None):
    await send_with_bomb("Привет - и тебе привет!\nМаксим - он тут админ\n/пред - (только для администраторов!) выдать "
                         "пред. Надо переслать сообщение юзера, которому надо дать пред\n/всепреды - посмотреть все "
                         "преды. Администраторам доступен просмотр предов всех юзеров, обычным юзерам - только своих. "
                         "Надо переслать сообщение, преды чьего юзера просмотреть\n/voteban с пересланным сообщением - "
                         "открыть голосование за бан участника\n/инфодоступ - разрешен ли доступ к написанию сообщений "
                         "в данный момент\n/профиль - посмотреть свой профиль\n/контакты - ссылки на связь с "
                         "разработчиком", message.peer_id, expire_ttl="120")


@bp.on.message_handler(AccessForAllRule(), text="/voteban", lower=True)
async def voteban_message(message: Message, _: Optional[User] = None):
    if message.reply_message:
        await check_or_create(message.reply_message.from_id, message.peer_id)
        if is_replied_self(message):
            await message("Просто попроси бана себе, а")

        else:
            poll = await create_poll(f"Голосование за бан пользователя с ID {message.reply_message.from_id}",
                                     True, False, ["За", "Против"], False)

            await message(attachment=f"poll{poll['owner_id']}_{poll['id']}")

    else:
        await message(
            "Перешли сообщение человека, за которого начать голосование за бан!"
        )


@bp.on.message_handler(text="/инфодоступ", lower=True)
async def check_access_message(message: Message, _: Optional[User] = None):
    access = "разрешён" if access_for_all else "запрещён"
    await message(f"Доступ к написанию сообщений {access}")


@bp.on.message_handler(AccessForAllRule(), text="/контакты", lower=True)
async def get_contacts(message: Message, _: Optional[User] = None):
    name = (await BOT.api.users.get(message.from_id))[0].first_name
    await message(
        "[id{0}|{1}], список контактов с разработчиком:\nVK: vk.com/jottyfounder\nMail: "
        "vladislavbusiness@jottymdbbot.xyz\nПредложения по боту писать на почту.".format(
            message.from_id, name
        )
    )
