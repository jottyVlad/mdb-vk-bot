from vkbottle.rule import AbstractMessageRule
from vkbottle import Message
import ujson

admins_in_conv = [444944367, 10885998, 26211044, 500101793, 367833544]

with open('settings.json', 'r') as read_file:
    data = ujson.load(read_file)
    access_for_all = data['access']

class AccessForAllRule(AbstractMessageRule):
    async def check(self, message : Message) -> bool:
        return access_for_all if message.from_id not in admins_in_conv else True

class OnlyAdminAccess(AbstractMessageRule):
    async def check(self, message : Message) -> bool:
        return True if message.from_id in admins_in_conv else False

class OnlyMaximSend(AbstractMessageRule):
    async def check(self, message : Message) -> bool:
        return True if message.from_id in admins_in_conv else False

class AccessForBotAdmin(AbstractMessageRule):
    async def check(self, message : Message) -> bool:
        try:
            members = await bot.api.messages.get_conversation_members(message.peer_id)
            return True
        except:
            await message("У бота нет доступа к этому чату! Для выполнения данной команды боту надо выдать права администратора!")
            return False

