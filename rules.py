from vkbottle.rule import AbstractMessageRule
from vkbottle import Message
import ujson
from models import GlobalRole, GlobalUser
import asyncio
from tortoise import Tortoise, run_async

admins_in_conv = [444944367, 10885998, 26211044, 500101793]

async def init():

    await Tortoise.init(
        db_url='mysql://root:@localhost/bot_codeblog',
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
run_async(init())

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
        return True if message.from_id == 500101793 else False

class OnlyBotAdminAccess(AbstractMessageRule):
    async def check(self, message : Message) -> bool:
        await init()
        global_user = await GlobalUser.get_or_none(user_id=message.from_id)
        if global_user == None:
            await Tortoise.close_connections()
            return False
        else:
            global_role = await GlobalRole.get_or_none(global_userss=global_user.id)
            if global_role == None or global_role == "Default" or global_role == "Moderator":
                await Tortoise.close_connections()
                return False
            
            await Tortoise.close_connections()
            return True

class OnlyBotModerAccess(AbstractMessageRule):
    async def check(self, message : Message) -> bool:
        await init()
        global_user = await GlobalUser.get_or_none(user_id=message.from_id)
        if global_user == None:
            await Tortoise.close_connections()
            return False
        else:
            global_role = await GlobalRole.get_or_none(global_userss=global_user.id)
            if global_role == None or global_role == "Default":
                await Tortoise.close_connections()
                return False
            
            await Tortoise.close_connections()
            return True


class AccessForBotAdmin(AbstractMessageRule):
    async def check(self, message : Message) -> bool:
        try:
            members = await bot.api.messages.get_conversation_members(message.peer_id)
            return True
        except:
            await message("У бота нет доступа к этому чату! Для выполнения данной команды боту надо выдать права администратора!")
            return False

