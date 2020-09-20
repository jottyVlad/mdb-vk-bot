from vkbottle import User as vkBottleUser, Bot, Message
from config import ACCESS_TOKEN, USER_ACCESS_TOKEN
from models import *
import typing
import asyncio
import ujson

BOT = Bot(ACCESS_TOKEN, loop=asyncio.get_event_loop(), group_id=196816306)
USER = vkBottleUser(USER_ACCESS_TOKEN)

async def is_mention(mention: str) -> typing.Tuple[bool, str]:
    if all(char in mention for char in "[|]") and any(
        word in mention for word in ("id", "club")
    ):
        if "club" in mention:
            mention = mention[5:]
        else:
            mention = mention[3:]
        mention = int(mention.split("|")[0])
        return (True, mention)

    else:
        return (False, "")

async def check_or_create(
    user_id: int, peer_id: int, warns: int = 0
) -> typing.Tuple[User, GlobalUser]:

    """
        CHECK FOR USER IN CURRENT CHAT 
        AND GLOBAL USER IN DATABASE 
        AND RETURN USER'S PROFILE
        AND GLOBAL USER'S PROFILE 
    """
    profile = await User.get_or_none(user_id=user_id, peer_id=peer_id)
    global_profile = await GlobalUser.get_or_none(user_id=user_id)
    if profile == None:
        await User(user_id=user_id, peer_id=peer_id, warns=warns).save()
        profile = await User.get(user_id=user_id, peer_id=peer_id)

    if global_profile == None:
        default_role = await GlobalRole.get(name="Default")
        await GlobalUser(user_id=user_id, global_role=default_role).save()
        global_profile = GlobalUser.get(user_id=user_id)

    return (profile, global_profile)

async def get_access_for_all() -> bool:
    with open("settings.json", "r") as read_file:
        data = ujson.load(read_file)
        access_for_all = data["access"]
    
    return access_for_all

access_for_all = asyncio.get_event_loop().run_until_complete(get_access_for_all())

