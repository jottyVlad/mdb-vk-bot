import asyncio
import typing

import ujson
from PIL import (
    Image, ImageDraw, ImageFont
)
from vkbottle import User as vkBottleUser, Bot

from config import ACCESS_TOKEN, USER_ACCESS_TOKEN
from models import *

BOT = Bot(ACCESS_TOKEN, loop=asyncio.get_event_loop(), group_id=196816306)
USER = vkBottleUser(USER_ACCESS_TOKEN)

#TODO: создать utils.py и переместить туда функции
#TODO: remove async
async def is_mention(mention: str) -> typing.Union[typing.Tuple[bool, int], typing.Tuple[bool, str]]:
    if all(char in mention for char in "[|]") and any(
            word in mention for word in ("id", "club")
    ):
        if "club" in mention:
            mention = mention[5:]
        else:
            mention = mention[3:]
        mention = int(mention.split("|")[0])
        return True, mention

    else:
        return False, ""


async def check_or_create(
        user_id: int, peer_id: int, warns: int = 0
) -> typing.Tuple[User, GlobalUser]:
    #TODO: make it down and delete tabs
    """
        CHECK FOR USER IN CURRENT CHAT 
        AND GLOBAL USER IN DATABASE 
        AND RETURN USER'S PROFILE
        AND GLOBAL USER'S PROFILE 
    """
    profile = await User.get_or_none(user_id=user_id, peer_id=peer_id)
    if profile is None:
        await User(user_id=user_id, peer_id=peer_id, warns=warns).save()
        profile = await User.get(user_id=user_id, peer_id=peer_id)

    global_profile = await GlobalUser.get_or_none(user_id=user_id)
    if global_profile is None:
        default_role = await GlobalRole.get(name="Default")
        await GlobalUser(user_id=user_id, global_role=default_role).save()
        global_profile = GlobalUser.get(user_id=user_id)

    return profile, global_profile


async def get_access_for_all() -> bool:
    with open("settings.json", "r") as read_file:
        data = ujson.load(read_file)
        access_for_all = data["access"]

    return access_for_all


access_for_all = asyncio.get_event_loop().run_until_complete(get_access_for_all())


async def make_profile_photo(user: User):
    #TODO: все цифры в константы с понятным описанием
    x, y = 30, 50
    color = (0, 0, 0)

    global_user = await GlobalUser.get_or_none(user_id=user.user_id)
    global_role = await GlobalRole.get(global_userss=global_user.id)

    img = Image.open('profile_photo.jpg')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('Tahoma.ttf', 30)
    draw.text((x, y), f"Ваш ID: {user.user_id}", color, font=font)
    y += 35
    draw.text((x, y), f"Ваша роль: {global_role}", color, font=font)
    y += 35
    draw.text((x, y), f"Деньги: {user.coins}", color, font=font)
    y += 35
    draw.text((x, y), f"Энергия: {user.energy}", color, font=font)
    y += 35
    draw.text((x, y), f"EXP: {user.exp}", color, font=font)
    y += 35
    job = "безработный"
    if user.work_id_id is not None:
        job = (await Work.get(id=user.work_id_id)).name

    car = "отсутствует"
    if user.car_id is not None:
        car = (await Car.get(id=user.car_id)).name

    draw.text((x, y), f"Работа: {job}", color, font=font)
    y += 35
    draw.text((x, y), f"Машина: {car}", color, font=font)
    y += 35
    draw.text((x, y), f"Количество предупреждений: {user.warns}", color, font=font)
    img.save(f"{user.user_id}.jpeg")
