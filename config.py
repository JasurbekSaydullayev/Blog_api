from dotenv import dotenv_values
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
config = dotenv_values(dotenv_path)

TOKEN = config["TOKEN"]

DATABASE_URL = config["DATABASE_URL"]

ADMIN_USERNAME = config["ADMIN_USERNAME"]

ADMIN_PASSWORD = config["ADMIN_PASSWORD"]
