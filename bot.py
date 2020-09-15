from aiohttp import web
from config import SECRET
import ujson
from tortoise import Tortoise, run_async
import aiohttp_jinja2
import jinja2
from pathlib import Path
from global_settings import *
from routes import actions, admin_realize, global_admin_realize, users_realize

index_dir = str(Path(__file__).resolve().parent)+'/index_page'

async def init():
    """
        INIT SQLITE3 DATABASE
    """
    await Tortoise.init(
        db_url="sqlite://mdbbot_database.sqlite3", modules={"models": ["models"]}
    )
    await Tortoise.generate_schemas()

BOT.loop.run_until_complete(init())
BOT.set_blueprints(actions.bp, admin_realize.bp, global_admin_realize.bp, users_realize.bp)

with open("settings.json", "r") as read_file:
    data = ujson.load(read_file)
    access_for_all = data["access"]

app = web.Application()
routes = web.RouteTableDef()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(str(index_dir)))
app.router.add_static('/static/',
                      path=str('/botenv/index_page/'),
                      name='static')

@routes.get("/")
@aiohttp_jinja2.template('index.html')
async def hello(request):
    """
        ROOT SITE RESPONSE
    """
    return {}

@routes.get("/when_update")
@aiohttp_jinja2.template('whenupdate.html')
async def whenupdate(request):
    """
        WHENUPDATE SITE RESPONSE
    """
    return {}

@routes.get("/changelog")
@aiohttp_jinja2.template('changelog.html')
async def changelog(request):
    """
        WHENUPDATE SITE RESPONSE
    """
    return {}

@routes.post("/bot")
async def bot_execute(request):
    """
        BOT REQUEST RESPONSE
    """
    event = await request.json()
    emulation = await BOT.emulate(event, confirmation_token="e826056e", secret=SECRET)
    return web.Response(text=emulation)

app.add_routes(routes)
web.run_app(app, host="0.0.0.0", port=80)