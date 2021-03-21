import datetime
import sys
from typing import Optional

from vkbottle.bot import Blueprint

from models import Work, Car, Conversation
from utils.consts import CAR_COST_MULTIPLIER, BuyCarUserStatuses
from utils.main import status_on_buy_car
from utils.rules import *

sys.path.append("..")

bp = Blueprint(name="Working with economic system")


@bp.on.message_handler(AccessForAllRule(), Registered(), text="/дать_работу <j_id>")
async def give_job(message: Message, user: User, j_id: str = None):
    if j_id.isdigit():
        j_id = int(j_id)
        work = await Work.get(id=j_id)
        chat = await Conversation.get(peer_id=message.peer_id)
        await User.get(user_id=user.user_id, chat=chat).update(
            work=work, job_lp=datetime.datetime.now()
        )
        await message("Работа выдана!")
    else:
        await message("Введите число!")


@bp.on.message_handler(AccessForAllRule(), Registered(), text="/получить_зп")
async def take_salary(message: Message, user: User):
    if (await user.work) is not None:
        if user.job_lp.timestamp() <= (datetime.datetime.now() - datetime.timedelta(0, 0, 0, 0, 0, 24)).timestamp():
            work = await Work.get(id=(await user.work).id)
            await User.get(user_id=user.user_id, chat=(await user.chat)).update(
                coins=user.coins + work.salary,
                job_lp=datetime.datetime.now(),
            )

            await message("Зарплата выдана!")
        else:
            time = datetime.datetime(user.job_lp.year, user.job_lp.month, user.job_lp.day,
                                     user.job_lp.hour, user.job_lp.minute, user.job_lp.second,
                                     user.job_lp.microsecond) - \
                   (datetime.datetime.now() + datetime.timedelta(0, 0, 0, 0, 0, 24))
            await message(f"Осталось до получения зарплаты: {str(time).split(', ')[1].split('.')[0]}")
    else:
        await message("У вас нет работы!")


@bp.on.message_handler(text="/список_работ")
async def job_list(message: Message):
    jobs = await Work.all()
    await message(
        "\n".join(
            [f"ID: {job.id}; Название: {job.name}; ЗП: {job.salary}" for job in jobs]
        )
    )


@bp.on.message_handler(text="/список_машин")
async def job_list(message: Message):
    cars = await Car.all()
    await message(
        "\n".join(
            [f"ID: {car.id}; Название: {car.name}; Множитель: {car.multiplier}; Цена: {car.cost}" for car in cars]
        )
    )


@bp.on.message_handler(AccessForAllRule(), Registered(), text="/купить_машину <c_id>")
async def buy_car(message: Message, user: User, c_id: str = None):
    if c_id.isdigit():
        c_id = int(c_id)
        car = await Car.get(id=c_id)

        buy_car_user_status = status_on_buy_car(user, car)

        if buy_car_user_status == BuyCarUserStatuses.APPROVED:
            chat = await Conversation.get(peer_id=message.peer_id)
            await User.get(user_id=message.from_id, chat=chat).update(
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


@bp.on.message_handler(AccessForAllRule(), Registered(), text="/продать_машину")
async def sell_car(message: Message, user: User):
    if user.car_id is not None:
        car_cost = (await Car.get(id=user.car_id)).cost

        car_cost = car_cost - (car_cost * CAR_COST_MULTIPLIER)
        chat = await Conversation.get(peer_id=message.peer_id)
        await User.get(user_id=message.from_id, chat=chat).update(
            coins=user.coins + car_cost, car_id=None
        )
        await message("Машина продана!")
    else:
        await message("У вас нет машины!")
