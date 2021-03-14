import datetime
import sys
from threading import Thread
from typing import Optional

from tortoise import Tortoise
from vkbottle.bot import Blueprint

from global_settings import *
from models import Work, User, Car
from rules import *

sys.path.append("..")

bp = Blueprint(name="Working with economic system")


async def payouts():
    conn = Tortoise.get_connection("default")
    time_unix = int(datetime.datetime.now().timestamp() - 86400)

    users = await conn.execute_query_dict(
        "SELECT * FROM `users` WHERE `work_id_id` IS NOT NULL AND `job_lp` IS NOT NULL AND `job_lp` <= ?", [time_unix]
    )
    for user in users:
        work = await Work.get(id=user["work_id_id"])
        await User.get(user_id=user["user_id"], peer_id=user["peer_id"]).update(
            coins=user["coins"] + work.salary,
            job_lp=int(datetime.datetime.now().timestamp()),
        )


class PayoutsThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while True:
            try:
                loop.run_until_complete(payouts())
                loop.run_until_complete(asyncio.sleep(15))
            except Exception as _:
                continue


@bp.on.message_handler(AccessForAllRule(), text="/дать_работу <j_id>")
async def give_job(message: Message, _: Optional[User] = None, j_id: str = None):
    if j_id.isdigit():
        j_id = int(j_id)
        work = await Work.get(id=j_id)
        # TODO: затестить
        await User.get(user_id=message.from_id, peer_id=message.peer_id).update(
            work_id=work, job_lp=int(datetime.datetime.now().timestamp())
        )
        await message("Работа выдана!")
    else:
        await message("Введите число!")


@bp.on.message_handler(text="/список_работ")
async def job_list(message: Message, _: Optional[User] = None):
    jobs = await Work.all()
    await message(
        "\n".join(
            [f"ID: {job.id}; Название: {job.name}; ЗП: {job.salary}" for job in jobs]
        )
    )


@bp.on.message_handler(text="/список_машин")
async def job_list(message: Message, _: Optional[User] = None):
    cars = await Car.all()
    await message(
        "\n".join(
            [f"ID: {car.id}; Название: {car.name}; Множитель: {car.multiplier}" for car in cars]
        )
    )


@bp.on.message_handler(AccessForAllRule(), text="/купить_машину <c_id>")
async def buy_car(message: Message, user: Optional[User] = None, c_id: str = None):
    if c_id.isdigit():
        c_id = int(c_id)
        car = await Car.get(id=c_id)

        if user.coins >= car.cost and user.exp >= car.exp_need and user.car_id is None:
            await User.get(user_id=message.from_id, peer_id=message.peer_id).update(
                coins=user.coins - car.cost, car=car
            )
            # TODO: рассмотреть возможность вынести проверку в отдельный метод
            await message(f"Машина {car} куплена!")
        elif user.coins < car.cost:
            await message("У тебя недостаточно денег!")
        elif user.exp < car.exp_need:
            await message("У тебя недостаточно опыта!")
        else:
            await message("У тебя уже есть машина!")
    else:
        await message("Введите цифру-ID машины!")


@bp.on.message_handler(AccessForAllRule(), text="/продать_машину")
async def sell_car(message: Message, user: Optional[User] = None):
    if user.car_id is not None:
        car_cost = (await Car.get(id=user.car_id)).cost
        # TODO: число 0.1 в константу
        car_cost = car_cost - (car_cost * 0.1)
        await User.get(user_id=message.from_id, peer_id=message.peer_id).update(
            coins=user.coins + car_cost, car_id=None
        )
        await message("Машина продана!")
    else:
        await message("У вас нет машины!")
