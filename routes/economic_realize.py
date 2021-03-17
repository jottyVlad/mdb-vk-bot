import datetime
import sys
from threading import Thread
from typing import Optional

from tortoise import Tortoise
from vkbottle.bot import Blueprint

from global_settings import *
from models import Work, User, Car
from utils.main import status_on_buy_car
from utils.rules import *
from utils.consts import CAR_COST_MULTIPLIER, BuyCarUserStatuses

sys.path.append("..")

bp = Blueprint(name="Working with economic system")


@bp.on.message_handler(AccessForAllRule(), text="/дать_работу <j_id>")
async def give_job(message: Message, _: Optional[User] = None, j_id: str = None):
    if j_id.isdigit():
        j_id = int(j_id)
        work = await Work.get(id=j_id)
        await User.get(user_id=message.from_id, peer_id=message.peer_id).update(
            work_id=work, job_lp=int(datetime.datetime.now().timestamp())
        )
        await message("Работа выдана!")
    else:
        await message("Введите число!")


@bp.on.message_handler(AccessForAllRule(), text="/получить_зп")
async def take_salary(message: Message, user: Optional[User] = None):
    if user.work_id is not None:
        if user.job_lp <= int(datetime.datetime.now().timestamp() - 86400):
            work = await Work.get(id=user.work_id)
            await User.get(user_id=user.user_id, peer_id=user.chat).update(
                coins=user.coins + work.salary,
                job_lp=int(datetime.datetime.now().timestamp()),
            )

            await message("Зарплата выдана!")
        else:
            await message(f"Осталось до получения зарплаты: "
                          f"{user.job_lp + 86400 - datetime.datetime.now().timestamp()}")
    else:
        await message("У вас нет работы!")


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

        buy_car_user_status = status_on_buy_car(user, car)

        if buy_car_user_status == BuyCarUserStatuses.APPROVED:
            await User.get(user_id=message.from_id, peer_id=message.peer_id).update(
                coins=user.coins - car.cost, car=car
            )

            await message(f"Машина {car} куплена!")
        elif buy_car_user_status == BuyCarUserStatuses.NOT_ENOUGH_MONEY:
            await message("У тебя недостаточно денег!")
        elif buy_car_user_status == BuyCarUserStatuses.NOT_ENOUGH_EXP:
            await message("У тебя недостаточно опыта!")
        else:
            await message("У тебя уже есть машина!")
    else:
        await message("Введите цифру-ID машины!")


@bp.on.message_handler(AccessForAllRule(), text="/продать_машину")
async def sell_car(message: Message, user: Optional[User] = None):
    if user.car_id is not None:
        car_cost = (await Car.get(id=user.car_id)).cost

        car_cost = car_cost - (car_cost * CAR_COST_MULTIPLIER)
        await User.get(user_id=message.from_id, peer_id=message.peer_id).update(
            coins=user.coins + car_cost, car_id=None
        )
        await message("Машина продана!")
    else:
        await message("У вас нет машины!")
