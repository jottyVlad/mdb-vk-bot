import pathlib

import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp import web

import utils.consts
from config import SECRET, WEBHOOK_ACCEPT, CONFIRMATION_TOKEN
from routes import actions, admin_realize, global_admin_realize, users_realize, economic_realize
from utils.db_methods import init_database

INDEX_DIR = str(pathlib.Path(__file__).resolve().parent) + '/index_page'

utils.consts.BOT.loop.run_until_complete(init_database())
utils.consts.BOT.set_blueprints(
    actions.bp, admin_realize.bp, global_admin_realize.bp,
    users_realize.bp, economic_realize.bp
)

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
        emulation = await utils.consts.BOT.emulate(event, confirmation_token=CONFIRMATION_TOKEN, secret=SECRET)
        return web.Response(text=emulation)


APP.add_routes(ROUTES)
web.run_app(APP, host="127.0.0.1", port=8000)
