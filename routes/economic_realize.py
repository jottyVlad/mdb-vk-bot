import sys
import asyncio
import datetime
from threading import Thread
from typing import Optional

from tortoise import Tortoise
from vkbottle.bot import Blueprint

from rules import *
from models import User, Work
from global_settings import *


sys.path.append("..")

bp = Blueprint(name="Working with economic system")


async def payouts():

    conn = Tortoise.get_connection("default")
    time_unix = int(datetime.datetime.now().timestamp() - 86400)

    users = await conn.execute_query_dict(
        f"SELECT * FROM `users` WHERE `work_id_id` IS NOT NULL AND `job_lp` IS NOT NULL AND `job_lp` <= {time_unix}"
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
        user = await User.get(user_id=message.from_id, peer_id=message.peer_id).update(
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
            [f"ID: {car.multiplier}; Название: {car.multiplier}; Множитель: {car.multiplier}" for car in cars]
        )
    )
