import sys

from vkbottle.bot import Blueprint

from global_settings import *
from models import User
from rules import *


sys.path.append("..")
bp = Blueprint(name="Working with admin functions")


@bp.on.message_handler(OnlyAdminAccess(), AccessForBotAdmin(), text="бан", lower=True)
async def bot_ban_message(message: Message):
    await check_or_create(message.from_id, message.peer_id)
    if message.reply_message:
        await message(
            f"ПОДТВЕРДИТЕ БАН ПОЛЬЗОВАТЕЛЯ С ID {message.reply_message.from_id}! НАПИШИТЕ 'ЗАБАНИТЬ' (ЗАГЛАВНЫМИ БУКВАМИ) ДЛЯ ТОГО, ЧТОБЫ ЗАБАНИТЬ, ИЛИ 'ВЫЙТИ' (ЗАГЛАВНЫМИ), ЧТОБЫ ВЫЙТИ ИЗ ЭТОГО МЕНЮ!"
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
            f"ПОДТВЕРДИТЕ БАН ПОЛЬЗОВАТЕЛЯ С ID {user_id}! НАПИШИТЕ 'ЗАБАНИТЬ' (ЗАГЛАВНЫМИ БУКВАМИ) ДЛЯ ТОГО, ЧТОБЫ ЗАБАНИТЬ, ИЛИ 'ВЫЙТИ' (ЗАГЛАВНЫМИ), ЧТОБЫ ВЫЙТИ ИЗ ЭТОГО МЕНЮ!"
        )


@bp.on.chat_message(OnlyAdminAccess(), text="/пред <mention> <count>", lower="True")
async def warn_with_mention_message(message: Message, mention: str, count: str):
    if (await is_mention(mention))[0]:
        mention = (await is_mention(mention))[1]
    else:
        await message("Я не вижу упоминания! Упоминание обязательно!")
        return

    if (not count.isdigit()) and not (count.startswith("-") and count[1:].isdigit()):
        await message("Текст вместо цифры?.. М-да...")
    else:
        count = int(count)
        if count > 4:
            await check_or_create(message.from_id, message.peer_id)
            await message(
                "Да куда ты разогнался, больше 4 варнов кидать чуваку, тут максимум 4 варна есть, конч админ кароч"
            )
        else:
            user_in_db = await User.get_or_none(
                user_id=mention, peer_id=message.peer_id
            )
            if user_in_db == None and count < 0:
                await check_or_create(mention, message.peer_id)
                await message(
                    "Ну нет у этого юзера предов. Ну не могу я забрать то, чего НЕТУ!!"
                )
            elif user_in_db == None and count > 0:
                await check_or_create(message.from_id, message.peer_id, count)
                await message(
                    f"Предупреждение выдано пользователю с ID {mention}, общее количество: {count}"
                )
            elif user_in_db != None:
                await check_or_create(message.from_id, message.peer_id)
                current_warns = user_in_db.warns
                if current_warns + count < 0:
                    await message(
                        f"Предупреждение НЕ выдано, т.к. при забирании такого кол-ва варнов у него будет меньше 0 варнов, что невозможно! Общее количество предов: {current_warns}"
                    )
                else:
                    updated_user = await User.get(
                        user_id=mention, peer_id=message.peer_id
                    ).update(warns=current_warns + count)
                    if current_warns + count >= 4:
                        await message(
                            f"Предупреждение выдано, общее количество больше или равно 4, требуется бан пользователя! Общее количество предов: {current_warns+count}"
                        )
                    else:
                        await message(
                            f"Предупреждение выдано, общее количество: {current_warns+count}"
                        )


@bp.on.chat_message(OnlyAdminAccess(), text="/пред <count>", lower="True")
async def warn_with_reply_message(message: Message, count: str):
    if message.reply_message:
        await check_or_create(message.from_id, message.peer_id)
        if (not count.isdigit()) and not (
            count.startswith("-") and count[1:].isdigit()
        ):
            await message("Текст вместо цифры?.. М-да...")
        else:
            count = int(count)
            if count > 4:
                await message(
                    "Да куда ты разогнался, больше 4 варнов кидать чуваку, тут максимум 4 варна есть, конч админ кароч"
                )
            else:
                user_in_db = await User.get_or_none(
                    user_id=message.reply_message.from_id, peer_id=message.peer_id
                )
                if user_in_db == None and count < 0:
                    await check_or_create(mention, message.peer_id)
                    await message(
                        "Ну нет у этого юзера предов. Ну не могу я забрать то, чего НЕТУ!!"
                    )
                elif user_in_db == None and count > 0:
                    await check_or_create(
                        message.reply_message.from_id, message.peer_id, count
                    )
                    await message(
                        f"Предупреждение выдано пользователю с ID {message.reply_message.from_id}, общее количество: {count}"
                    )
                elif user_in_db != None:
                    await check_or_create(
                        message.reply_message.from_id, message.peer_id
                    )
                    current_warns = user_in_db.warns
                    if current_warns + count < 0:
                        await message(
                            f"Предупреждение НЕ выдано, т.к. при забирании такого кол-ва варнов у него будет меньше 0 варнов, что невозможно! Общее количество предов: {current_warns}"
                        )
                    else:
                        updated_user = await User.get(
                            user_id=message.reply_message.from_id,
                            peer_id=message.peer_id,
                        ).update(warns=current_warns + count)
                        if current_warns + count >= 4:
                            await message(
                                f"Предупреждение выдано, общее количество больше или равно 4, требуется бан пользователя! Общее количество предов: {current_warns+count}"
                            )
                        else:
                            await message(
                                f"Предупреждение выдано, общее количество: {current_warns+count}"
                            )

    else:
        await message("Хоть бы сообщение того, кого варнить надо, переслал бы")
