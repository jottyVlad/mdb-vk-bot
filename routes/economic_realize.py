import sys
sys.path.append('..')

import asyncio
from models import User, Work
from global_settings import *
from tortoise import Tortoise
import datetime
from vkbottle.bot import Blueprint
from threading import Thread
from rules import *

bp = Blueprint(name="Working with economic system")

async def payouts():

        conn = Tortoise.get_connection("default")
        time_unix = int(datetime.datetime.now().timestamp() - 86400)
        #users = await conn.execute_query_dict(f"SELECT * FROM `users` WHERE `work_id_id` != NULL AND `job_lp` != NULL and `job_lp` >= {time_unix}")
        users = await conn.execute_query_dict(f"SELECT * FROM `users` WHERE `work_id_id` IS NOT NULL AND `job_lp` IS NOT NULL AND `job_lp` <= {time_unix}")
        for user in users:
            work = await Work.get(id=user['work_id_id'])
            await User.get(user_id=user['user_id'], peer_id=user['peer_id']).update(coins=user['coins']+work.salary, job_lp=int(datetime.datetime.now().timestamp()))

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
            except:
                continue

@bp.on.message_handler(OnlyMaximSend(), text="/дать_работу <j_id>")
async def give_job(message: Message, j_id: str):
    if j_id.isdigit(): 
        j_id = int(j_id)
        work = await Work.get(id=j_id)
        user = await User.get(user_id=message.from_id, peer_id=message.peer_id).update(work_id=work, job_lp=int(datetime.datetime.now().timestamp()))
        await message("Работа выдана!")
    else:
        await message("Введите число!")

@bp.on.message_handler(text="/список_работ")
async def job_list(message: Message):
    jobs = await Work.all()
    await message('\n'.join([f"ID: {job.id}; Название: {job.name}; ЗП: {job.salary}" for job in jobs]))
    
