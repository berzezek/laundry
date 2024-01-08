import os
import dotenv

dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

DELIVERY_SERVICE_API_URL = os.getenv("DELIVERY_SERVICE_API_URL")

ADMIN_USERS = os.getenv("ADMIN_USERS").split(",")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))