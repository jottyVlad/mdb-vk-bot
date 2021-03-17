import pathlib

import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp import web

import global_settings
from config import SECRET, WEBHOOK_ACCEPT, CONFIRMATION_TOKEN
from routes import actions, admin_realize, global_admin_realize, users_realize, economic_realize
from utils.db_methods import init_database

INDEX_DIR = str(pathlib.Path(__file__).resolve().parent) + '/index_page'

global_settings.BOT.loop.run_until_complete(init_database())
global_settings.BOT.set_blueprints(
    actions.bp, admin_realize.bp, global_admin_realize.bp,
    users_realize.bp, economic_realize.bp
)

THREAD = economic_realize.PayoutsThread()
THREAD.start()

APP = aiohttp.web.Application()
ROUTES = aiohttp.web.RouteTableDef()

if not WEBHOOK_ACCEPT:
    aiohttp_jinja2.setup(APP, loader=jinja2.FileSystemLoader(str(INDEX_DIR)))
    APP.router.add_static('/static/',
                          path=str('./index_page/'),
                          name='static')


@ROUTES.get("/")
@aiohttp_jinja2.template('index.html')
async def hello(request):
    """Root site response"""
    return {}


@ROUTES.get("/when_update")
@aiohttp_jinja2.template('whenupdate.html')
async def whenupdate(request):
    """When update site response"""
    return {}


@ROUTES.get("/changelog")
@aiohttp_jinja2.template('changelog.html')
async def changelog(request):
    """Changelog site response"""
    return {}


@ROUTES.post("/bot")
async def bot_execute(request):
    """Bot request response"""
    if WEBHOOK_ACCEPT:
        return web.Response(text=CONFIRMATION_TOKEN)
    else:
        event = await request.json()
        emulation = await global_settings.BOT.emulate(event, confirmation_token=CONFIRMATION_TOKEN, secret=SECRET)
        return web.Response(text=emulation)


APP.add_routes(ROUTES)
web.run_app(APP, host="0.0.0.0", port=80)
