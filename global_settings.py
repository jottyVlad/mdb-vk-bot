import asyncio

from utils.main import get_access_for_all

access_for_all = asyncio.get_event_loop().run_until_complete(get_access_for_all())
