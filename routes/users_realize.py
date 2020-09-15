import sys
sys.path.append('..')

from vkbottle.bot import Blueprint
from global_settings import *
from models import Conversation, User, GlobalUser, GlobalRole
from rules import *
import random

bp = Blueprint(name="Working with users functions")

@bp.on.message_handler(
    AccessForAllRule(), text="привет", lower=True
)
async def hi_message(ans: Message):
    await check_or_create(ans.from_id, ans.peer_id)
    print(ans.peer_id)
    await ans("Привет, чувачелла")


@bp.on.message_handler(AccessForAllRule(), text="максим", lower=True)
async def maxim_message(ans: Message):
    await check_or_create(ans.from_id, ans.peer_id)
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
async def mda_message(ans: Message):
    await check_or_create(ans.from_id, ans.peer_id)
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
async def profile_message(message: Message):
    if message.reply_message and ((message.from_id in admins_in_conv) or message.reply_message.from_id == message.from_id):
        profile = (
            await check_or_create(message.reply_message.from_id, message.peer_id)
        )[0]

    elif message.reply_message and message.from_id not in admins_in_conv:
        await check_or_create(message.from_id, message.peer_id)
        await message("Доступ запрещен!")
        return
    else:
        profile = (await check_or_create(message.from_id, message.peer_id))[0]

    global_user = await GlobalUser.get_or_none(user_id=profile.user_id)
    global_role = await GlobalRole.get(global_userss=global_user.id)

    await message(
        "Ваш ID пользователя: {0}\nГлобальная роль: {1}\nКоличество предупреждений: {2}\nКоличество денег: ${3}\nЭнергия: {4}/5".format(
            profile.user_id, global_role, profile.warns, profile.coins, profile.energy
        )
    )

@bp.on.chat_message(AccessForAllRule(), text="/всепреды", lower=True)
async def watch_all_warns(message: Message):
    if not message.reply_message:
        user_in_db = await User.get_or_none(
            user_id=message.from_id, peer_id=message.peer_id
        )
        await check_or_create(message.from_id, message.peer_id)
        if user_in_db == None or user_in_db.count == 0:
            if user_in_db == None:
                user_in_db = await User(
                    user_id=message.reply_message.from_id, peer_id=message.peer_id
                ).save()

            await message(
                f"У пользователя с ID {message.from_id} отсутствуют предупреждения!\nКоманда предлагается к удалению!"
            )
        else:
            await message(
                f"Количество предупреждений у пользователя с ID {message.from_id}: {user_in_db.warns}\nКоманда предлагается к удалению!"
            )

    if (
        message.from_id not in admins_in_conv
        and message.reply_message.from_id != message.from_id
    ):
        await check_or_create(message.from_id, message.peer_id)
        await message(
            "Тебе доступ сюда запрещен, понимаешь? Надеюсь, да. **Тихо* Опять эти дауны меня не по назначению юзают* :(\nКоманда предлагается к удалению!"
        )
    else:
        await check_or_create(message.from_id, message.peer_id)
        await check_or_create(message.reply_message.from_id, message.peer_id)
        user_in_db = await User.get_or_none(
            user_id=message.reply_message.from_id, peer_id=message.peer_id
        )
        if user_in_db != None and user_in_db.warns != 0:
            await message(
                f"Количество предупреждений у пользователя с ID {message.reply_message.from_id}: {user_in_db.warns}\nКоманда предлагается к удалению!"
            )
        else:
            if user_in_db == None:
                user_in_db = await User(
                    user_id=message.reply_message.from_id, peer_id=message.peer_id
                ).save()
            await message(
                f"У пользователя с ID {message.reply_message.from_id} отсутствуют предупреждения!\nКоманда предлагается к удалению!"
            )

@bp.on.message_handler(AccessForAllRule(), text="/помощь", lower=True)
async def help_message(message: Message):
    await check_or_create(message.from_id, message.peer_id)
    await USER.api.request(
        "messages.send",
        {
            "message": "Привет - и тебе привет!\nМаксим - он тут админ\n/пред - (только для администраторов!) выдать пред. Надо переслать сообщение юзера, которому надо дать пред\n/всепреды - посмотреть все преды. Администраторам доступен просмотр предов всех юзеров, обычным юзерам - только своих. Надо переслать сообщение, преды чьего юзера просмотреть\n/voteban с пересланным сообщением - открыть голосование за бан участника\n/инфодоступ - разрешен ли доступ к написанию сообщений в данный момент\n/профиль - посмотреть свой профиль\n/контакты - ссылки на связь с разработчиком",
            "group_id": BOT.group_id,
            "peer_id": message.peer_id,
            "expire_ttl": "120",
            "random_id": random.randint(1, 1000000000000000),
        },
    )

@bp.on.message_handler(AccessForAllRule(), text="/voteban", lower=True)
async def voteban_message(message: Message):
    await check_or_create(message.from_id, message.peer_id)
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
async def check_access_message(message: Message):
    await check_or_create(message.from_id, message.peer_id)
    access = "разрешён" if global_settings.access_for_all else "запрещён"
    await message(f"Доступ к написанию сообщений {access}")

@bp.on.message_handler(AccessForAllRule(), text="/регистрация", lower=True)
async def registr_message(message: Message):
    profile = await User.get_or_none(user_id=message.from_id, peer_id=message.peer_id)
    global_profile = await GlobalUser.get_or_none(user_id=message.from_id)
    if profile != None:
        await message("Локальный профиль обнаружен")
    else:
        await User(user_id=message.from_id, peer_id=message.peer_id, warns=0).save()
        await message("Ваш локальный профиль успешно зарегистрирован")

    if global_profile != None:
        await message("Глобальный профиль обнаружен")
    else:
        default_role = await GlobalRole.get(name="Default")
        await GlobalUser(user_id=message.from_id, global_role=default_role).save()
        await message("Глобальный профиль успешно зарегистрирован")

@bp.on.message_handler(AccessForAllRule(), text="/контакты", lower=True)
async def get_contacts(message: Message):
    await check_or_create(message.from_id, message.peer_id)
    name = (await BOT.api.users.get(message.from_id))[0].first_name
    await message("[id{0}|{1}], список контактов с разработчиком:\nVK: vk.com/jottyfounder\nMail: vladislavbusiness@jottymdbbot.xyz\nПредложения по боту писать на почту."\
    .format(message.from_id, name))