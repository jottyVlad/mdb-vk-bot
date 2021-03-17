from vkbottle import Message
from vkbottle.rule import AbstractMessageRule

from config import ADMINS_IN_CONV
from global_settings import BOT
from models import GlobalRole, GlobalUser
from utils.main import get_access_for_all


class AccessForAllRule(AbstractMessageRule):
    async def check(self, message: Message) -> bool:
        return (await get_access_for_all()) if message.from_id not in ADMINS_IN_CONV else True


class OnlyAdminAccess(AbstractMessageRule):
    async def check(self, message: Message) -> bool:
        return message.from_id in ADMINS_IN_CONV


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
        if global_user is not None:
            global_role = str(await GlobalRole.get_or_none(global_userss=global_user.id))
            if global_role == "Administrator" or global_role == "Moderator":
                return True

        return False


class AccessForBotAdmin(AbstractMessageRule):
    async def check(self, message: Message) -> bool:
        try:
            await BOT.api.messages.get_conversation_members(message.peer_id)
            return True
        except Exception:
            await message("У бота нет доступа к этому чату! Для выполнения данной команды боту надо выдать права "
                          "администратора!")
            return False


class AccessForBotAdminAndSenderAdminOrConv(AbstractMessageRule):
    async def check(self, message: Message) -> bool:

        if message.from_id in ADMINS_IN_CONV:
            return True

        try:
            members = ((await BOT.api.messages.get_conversation_members(message.peer_id)).dict())['items']
            for member in members:
                if member['member_id'] == message.from_id and member['is_admin']:
                    return True

        except Exception:
            await message("У бота нет доступа к этому чату! Для выполнения данной команды боту надо выдать права "
                          "администратора!")

        return False
