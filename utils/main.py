import typing

import ujson
from PIL import Image, ImageDraw, ImageFont

from models import User, GlobalUser, GlobalRole, Work, Car
from utils.consts import START_WRITE_POSITION_X, START_WRITE_POSITION_Y, BLACK_COLOR


def is_mention(mention: str) -> typing.Union[typing.Tuple[bool, int], typing.Tuple[bool, str]]:
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
    """
    check for user in current chat
    and global user in database
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


async def make_profile_photo(user: User):
    x, y = START_WRITE_POSITION_X, START_WRITE_POSITION_Y

    global_user = await GlobalUser.get_or_none(user_id=user.user_id)
    global_role = await GlobalRole.get(global_userss=global_user.id)

    img = Image.open('profile_photo.jpg')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('Tahoma.ttf', 30)
    draw.text((x, y), f"Ваш ID: {user.user_id}", BLACK_COLOR, font=font)
    y += 35
    draw.text((x, y), f"Ваша роль: {global_role}", BLACK_COLOR, font=font)
    y += 35
    draw.text((x, y), f"Деньги: {user.coins}", BLACK_COLOR, font=font)
    y += 35
    draw.text((x, y), f"Энергия: {user.energy}", BLACK_COLOR, font=font)
    y += 35
    draw.text((x, y), f"EXP: {user.exp}", BLACK_COLOR, font=font)
    y += 35
    job = "безработный"
    if user.work_id_id is not None:
        job = (await Work.get(id=user.work_id_id)).name

    car = "отсутствует"
    if user.car_id is not None:
        car = (await Car.get(id=user.car_id)).name

    draw.text((x, y), f"Работа: {job}", BLACK_COLOR, font=font)
    y += 35
    draw.text((x, y), f"Машина: {car}", BLACK_COLOR, font=font)
    y += 35
    draw.text((x, y), f"Количество предупреждений: {user.warns}", BLACK_COLOR, font=font)
    img.save(f"{user.user_id}.jpeg")
