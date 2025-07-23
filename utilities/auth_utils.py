import os
from dotenv import load_dotenv

def get_app_password():
    load_dotenv()
    return os.getenv("APP_PASSWORD")
