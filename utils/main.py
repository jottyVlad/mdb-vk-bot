import random
import typing

import ujson
from PIL import Image, ImageDraw, ImageFont
from vkbottle.types.message import Message

from config import ADMINS_IN_CONV
from global_settings import USER, BOT
from models import User, GlobalUser, GlobalRole, Work, Car
from utils.consts import START_WRITE_POSITION_X, START_WRITE_POSITION_Y, BLACK_COLOR, MIN_RANDOM_ID_INT, \
    MAX_RANDOM_ID_INT
from utils.db_methods import check_or_create
from utils.errors import WrongWarnsCountException


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


def get_user_from_mention(mention: str) -> typing.Union[str, int]:
    if (is_mention(mention))[0]:
        mention = (is_mention(mention))[1]

    else:
        return ""

    return mention


async def send_with_bomb(text: str, peer_id: int, **kwargs):
    await USER.api.request(
        "messages.send",
        {
            "message": text,
            "group_id": BOT.group_id,
            "peer_id": peer_id,
            "expire_ttl": kwargs['ttl'] | "20",
            "random_id": random.randint(MIN_RANDOM_ID_INT, MAX_RANDOM_ID_INT),
        },
    )


async def create_poll(question: str, is_anonymous: bool,
                      is_multiply: bool, answers: typing.List[str], disable_unvote: bool) -> dict:
    poll = await USER.api.request(
        "polls.create",
        {
            "question": question,
            "is_anonymous": int(is_anonymous),
            "is_multiply": int(is_multiply),
            "add_answers": f'{answers}',
            "disable_unvote": int(disable_unvote),
        },
    )

    return poll


def is_replied_self(message: Message) -> bool:
    if (
            message.reply_message.from_id == message.from_id
            or message.reply_message.from_id in ADMINS_IN_CONV
            or message.reply_message.from_id == -BOT.group_id
    ):
        return True

    return False


async def give_warns(message: Message, user: typing.Optional[User], count: int) -> User:
    if user is None:
        if 4 >= count >= 0:
            await check_or_create(message.from_id, message.peer_id, count)
            user = await User.get(user_id=message.from_id, peer_id=message.peer_id)
            return user

        else:
            raise WrongWarnsCountException("Wrong count of giving warns")

    else:
        if 4 >= user.warns + count >= 0:
            await User.get(
                user_id=user.user_id, peer_id=message.peer_id
            ).update(warns=user.warns + count)

            user = await User.get(user_id=user.user_id, peer_id=message.peer_id)

            return user

        else:
            raise WrongWarnsCountException("Wrong count of giving warns")
