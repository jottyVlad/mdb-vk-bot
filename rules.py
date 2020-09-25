from vkbottle.rule import AbstractMessageRule
from vkbottle import Message
from models import GlobalRole, GlobalUser
import asyncio
from config import ACCESS_TOKEN, admins_in_conv
from vkbottle import Bot
from global_settings import get_access_for_all

bot = Bot(ACCESS_TOKEN)


class AccessForAllRule(AbstractMessageRule):
    async def check(self, message: Message) -> bool:
        return (await get_access_for_all()) if message.from_id not in admins_in_conv else True


class OnlyAdminAccess(AbstractMessageRule):
    async def check(self, message: Message) -> bool:
        return message.from_id in admins_in_conv


class OnlyMaximSend(AbstractMessageRule):
    async def check(self, message: Message) -> bool:
        return message.from_id == 500101793


class OnlyBotAdminAccess(AbstractMessageRule):
    async def check(self, message: Message) -> bool:
        global_user = await GlobalUser.get_or_none(user_id=message.from_id)
        if global_user is None:
            return False
        else:
            global_role = str(await GlobalRole.get_or_none(global_userss=global_user.id))
            if global_role == "Administrator":
                return True
            else:
                return False


class OnlyBotModerAccess(AbstractMessageRule):
    async def check(self, message: Message) -> bool:
        global_user = await GlobalUser.get_or_none(user_id=message.from_id)
        if global_user is None:
            return False
        else:
            global_role = str(await GlobalRole.get_or_none(global_userss=global_user.id))
            if global_role == "Administrator" or global_role == "Moderator":
                return True
            else:
                return False


class AccessForBotAdmin(AbstractMessageRule):
    async def check(self, message: Message) -> bool:
        try:
            await bot.api.messages.get_conversation_members(message.peer_id)
            return True
        except Exception as _:
            await message("У бота нет доступа к этому чату! Для выполнения данной команды боту надо выдать права "
                          "администратора!")
            return False


class AccessForBotAdminAndSenderAdminOrConv(AbstractMessageRule):
    async def check(self, message: Message) -> bool:
        if message.peer_id == 2000000002 and message.from_id in admins_in_conv:
            return True

        try:
            members = ((await bot.api.messages.get_conversation_members(message.peer_id)).dict())['items']
            for member in members:
                if member['member_id'] == message.from_id and member['is_admin'] == True: return True
                continue

            return False
        except Exception as e:
            await message("У бота нет доступа к этому чату! Для выполнения данной команды боту надо выдать права "
                          "администратора!")
            return False
