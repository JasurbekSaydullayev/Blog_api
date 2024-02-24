from aiogram import Bot, types, Router
from aiogram.filters import Command

from telegram_bot.filters.chat_types import ChatTypeFilter


user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(["group", "supergroup"]))
user_group_router.edited_message.filter(ChatTypeFilter(["group", "supergroup"]))


@user_group_router.message(Command("admin"))
async def get_admins(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    admins_list = await bot.get_chat_administrators(chat_id)
    for admin in admins_list:
        if not admin.user.id == message.from_user.id and admin.status == "creator":
            await message.reply("Siz guruhda katta admin emassiz")
            await message.delete()
            return
    admins_list = [
        member.user.id
        for member in admins_list
        if member.status == "creator" or member.status == "administrator"
    ]
    bot.my_admins_list = admins_list
    if message.from_user.id in admins_list:
        await message.delete()
