from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Loading token from .env
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
SECRET = os.getenv("SECRET")
USER_ACCESS_TOKEN = os.getenv("USER_ACCESS_TOKEN")
