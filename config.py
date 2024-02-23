from dotenv import dotenv_values

config = dotenv_values(".env")

DATABASE_URL = config["DATABASE_URL"]

ADMIN_USERNAME = config["ADMIN_USERNAME"]

ADMIN_PASSWORD = config["ADMIN_PASSWORD"]