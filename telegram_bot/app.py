import logging
import asyncio

from aiogram import Bot, Dispatcher, types

from handlers.user_group import user_group_router
from handlers.admin_private import admin_router

from config import TOKEN
from telegram_bot.common.bot_cmds_list import private

ALLOWED_UPDATES = ['message, edited_message']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(str(TOKEN))
bot.my_admins_list = []

dp = Dispatcher(logger=logger)

dp.include_router(user_group_router)
dp.include_router(admin_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

if __name__ == "__main__":
    asyncio.run(main())
