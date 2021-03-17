import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Loading token from .env
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
SECRET = os.getenv("SECRET")
USER_ACCESS_TOKEN = os.getenv("USER_ACCESS_TOKEN")
WEBHOOK_ACCEPT = bool(int(os.getenv("WEBHOOK_ACCEPT", 0)))
CONFIRMATION_TOKEN = os.getenv("CONFIRMATION_TOKEN")
NEW_START = bool(int(os.getenv("NEW_START", 0)))
ADMINS_IN_CONV = list(map(int, os.getenv("ADMINS_IN_CONV").split(',')))

BOT_GROUP_ID = 196816306
