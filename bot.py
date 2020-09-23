import pathlib

import aiohttp
import tortoise
import jinja2
import aiohttp_jinja2

import config
import tortoise_cfg
from routes import (actions, admin_realize, 
        global_admin_realize, users_realize, economic_realize
    )
import global_settings

INDEX_DIR = str(pathlib.Path(__file__).resolve().parent)+'/index_page'

async def init():
    """
        INIT SQLITE3 DATABASE
    """
    await tortoise.Tortoise.init(config=tortoise_cfg.TORTOISE_ORM)
    await tortoise.Tortoise.generate_schemas()

global_settings.BOT.loop.run_until_complete(init())
global_settings.BOT.set_blueprints(
        actions.bp, admin_realize.bp, global_admin_realize.bp, 
        users_realize.bp, economic_realize.bp
        )

THREAD = economic_realize.PayoutsThread()
THREAD.start()

APP = aiohttp.web.Application()
ROUTES = aiohttp.web.RouteTableDef()
aiohttp_jinja2.setup(APP, loader=jinja2.FileSystemLoader(str(INDEX_DIR)))
APP.router.add_static('/static/',
                      path=str('/botenv/index_page/'),
                      name='static')

@ROUTES.get("/")
@aiohttp_jinja2.template('index.html')
async def hello(request):
    """
        ROOT SITE RESPONSE
    """
    return {}

@ROUTES.get("/when_update")
@aiohttp_jinja2.template('whenupdate.html')
async def whenupdate(request):
    """
        WHENUPDATE SITE RESPONSE
    """
    return {}

@ROUTES.get("/changelog")
@aiohttp_jinja2.template('changelog.html')
async def changelog(request):
    """
        WHENUPDATE SITE RESPONSE
    """
    return {}

@ROUTES.post("/bot")
async def bot_execute(request):
    """
        BOT REQUEST RESPONSE
    """
    event = await request.json()
    emulation = await global_settings.BOT.emulate(
            event, confirmation_token="e826056e", secret=config.SECRET
            )
    return aiohttp.web.Response(text=emulation)

APP.add_routes(ROUTES)
aiohttp.web.run_app(APP, host="0.0.0.0", port=80)
