from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_URL")
ADMIN_KEY = os.getenv("ADMIN_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")