import sys
import random
import os
from typing import Optional

from vkbottle.bot import Blueprint
from vkbottle.ext import Middleware
import aiohttp
import ujson

from global_settings import *
from models import Conversation, User, GlobalUser, GlobalRole
from rules import *
from config import admins_in_conv, NEW_START

sys.path.append("..")
bp = Blueprint(name="Working with users functions")


@bp.on.message_handler(AccessForAllRule(), text="привет", lower=True)
async def hi_message(ans: Message, _: Optional[User] = None):
    await ans("Привет, чувачелла")


@bp.on.message_handler(AccessForAllRule(), text="максим", lower=True)
async def maxim_message(ans: Message, _: Optional[User] = None):
    await USER.api.request(
        "messages.send",
        {
            "message": "Максим админ тут да ага бота создаватель в беседе повеливатель ага да м-да...",
            "group_id": BOT.group_id,
            "peer_id": ans.peer_id,
            "expire_ttl": "20",
            "random_id": random.randint(-2e9, 2e9),
        },
    )


@bp.on.message_handler(AccessForAllRule(), text="мда", lower=True)
async def mda_message(ans: Message, _: Optional[User] = None):
    await USER.api.request(
        "messages.send",
        {
            "message": "Да мда конечно это такое мда что прямо м-да...",
            "group_id": BOT.group_id,
            "peer_id": ans.peer_id,
            "expire_ttl": "20",
            "random_id": random.randint(-2e9, 2e9),
        },
    )


@bp.on.message_handler(AccessForAllRule(), text=["/профиль", "/profile"], lower=True)
async def profile_message(message: Message, profile: Optional[User] = None):

    if message.reply_message and (
            (message.from_id not in admins_in_conv) or
            (message.from_id != message.reply_message.from_id)):

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


@bp.on.chat_message(AccessForAllRule(), text="/всепреды", lower=True)
async def watch_all_warns(message: Message, user: Optional[User] = None):
    if not message.reply_message:
        if user.warns == 0:

            await message(
                f"У пользователя с ID {message.from_id} отсутствуют предупреждения!\nКоманда предлагается к удалению!"
            )
        else:
            await message(
                f"Количество предупреждений у пользователя с ID {message.from_id}: {user.warns}\nКоманда предлагается "
                f"к удалению! "
            )

    if (
            message.from_id not in admins_in_conv
            and message.reply_message.from_id != message.from_id
    ):
        await message(
            "Тебе доступ сюда запрещен, понимаешь? Надеюсь, да. **Тихо* Опять эти дауны меня не по назначению юзают* "
            ":(\nКоманда предлагается к удалению! "
        )
    else:
        await check_or_create(message.reply_message.from_id, message.peer_id)
        user_from_message = await User.get_or_none(
            user_id=message.reply_message.from_id, peer_id=message.peer_id
        )
        if user_from_message is not None and user_from_message.warns != 0:
            await message(
                f"Количество предупреждений у пользователя с ID {message.reply_message.from_id}: "
                f"{user_from_message.warns}\nКоманда предлагается к удалению!"
            )
        else:
            if user_from_message is None:
                await User(
                    user_id=message.reply_message.from_id, peer_id=message.peer_id
                ).save()
            await message(
                f"У пользователя с ID {message.reply_message.from_id} отсутствуют предупреждения!\nКоманда "
                f"предлагается к удалению! "
            )


@bp.on.message_handler(AccessForAllRule(), text="/помощь", lower=True)
async def help_message(message: Message, _: Optional[User] = None):
    await USER.api.request(
        "messages.send",
        {
            "message": "Привет - и тебе привет!\nМаксим - он тут админ\n/пред - (только для администраторов!) выдать "
                       "пред. Надо переслать сообщение юзера, которому надо дать пред\n/всепреды - посмотреть все "
                       "преды. Администраторам доступен просмотр предов всех юзеров, обычным юзерам - только своих. "
                       "Надо переслать сообщение, преды чьего юзера просмотреть\n/voteban с пересланным сообщением - "
                       "открыть голосование за бан участника\n/инфодоступ - разрешен ли доступ к написанию сообщений "
                       "в данный момент\n/профиль - посмотреть свой профиль\n/контакты - ссылки на связь с "
                       "разработчиком",
            "group_id": BOT.group_id,
            "peer_id": message.peer_id,
            "expire_ttl": "120",
            "random_id": random.randint(-2e9, 2e9),
        },
    )


@bp.on.message_handler(AccessForAllRule(), text="/voteban", lower=True)
async def voteban_message(message: Message, _: Optional[User] = None):
    if message.reply_message:
        await check_or_create(message.reply_message.from_id, message.peer_id)
        if (
                message.reply_message.from_id == message.from_id
                or message.reply_message.from_id in admins_in_conv
                or message.reply_message.from_id == -BOT.group_id
        ):
            await message("Просто попроси бана себе, а")

        else:
            poll = await USER.api.request(
                "polls.create",
                {
                    "question": f"Голосование за бан пользователя с ID {message.reply_message.from_id}",
                    "is_anonymous": 1,
                    "is_multiply": 0,
                    "add_answers": '["За","Против"]',
                    "disable_unvote": 0,
                },
            )
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


@bp.on.message_handler(AccessForAllRule(), text="/купить_машину <c_id>")
async def buy_car(message: Message, c_id: str, user: Optional[User] = None):
    if c_id.isdigit():
        c_id = int(c_id)
        car = await Car.get(id=c_id)

        if user.coins >= car.cost and user.exp >= car.exp_need and user.car_id is None:
            await User.get(user_id=message.from_id, peer_id=message.peer_id).update(
                coins=user.coins - car.cost, car=car
            )
            await message(f"Машина {car} куплена!")
        elif user.coins < car.cost:
            await message("У тебя недостаточно денег!")
        elif user.exp < car.exp_need:
            await message("У тебя недостаточно опыта!")
        else:
            await message("У тебя уже есть машина!")
    else:
        await message("Введите цифру-ID машины!")


@bp.on.message_handler(AccessForAllRule(), text="/продать_машину")
async def sell_car(message: Message, user: Optional[User] = None):
    if user.car_id is not None:
        car_cost = (await Car.get(id=user.car_id)).cost
        car_cost = car_cost - (car_cost * 0.1)
        await User.get(user_id=message.from_id, peer_id=message.peer_id).update(
            coins=user.coins + car_cost, car_id=None
        )
        await message("Машина продана!")
    else:
        await message("У вас нет машины!")