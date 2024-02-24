from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from telegram_bot.filters.chat_types import ChatTypeFilter, IsAdmin
from telegram_bot.kbds.reply import get_keyboard
from database import SessionLocal
from models import User, Blog

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

ADMIN_KB = get_keyboard(
    "Foydalanuvchilar",
    "Bloglar",
    "Commentlar",
    placeholder="Harakatni tanlang",
    sizes=(2, 1),
)

FOYDALANUVCHILAR = get_keyboard(
    "Foydalanuvchilarni ko'rish",
    "Foydalanuvchini o'chirish",
    "Orqaga",
    placeholder="Harakatni tanlang",
    sizes=(2, 1,),
)

BLOGLAR = get_keyboard(
    "Bloglarni ko'rish",
    "Blogni o'chirish",
    "Orqaga",
    placeholder="Harakatni tanlang",
    sizes=(2, 1,),
)


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Nima qilishni xoxlaysiz?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Orqaga")
async def admin_orqaga(message: types.Message):
    await message.answer("Nima qilishni xoxlaysiz?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Foydalanuvchilar")
async def users_actions(message: types.Message):
    await message.answer("Harakatni tanlang", reply_markup=FOYDALANUVCHILAR)


@admin_router.message(F.text == "Bloglar")
async def blogs_actions(message: types.Message):
    await message.answer("Harakatni tanlang", reply_markup=BLOGLAR)


@admin_router.message(F.text == "Bloglarni ko'rish")
async def blogs(message: types.Message):
    db = SessionLocal()
    blogs = db.query(Blog).all()
    await message.answer("Bloglar: ", reply_markup=BLOGLAR)
    for blog in blogs:
        await message.answer(f"Blog ID si: {blog.id}\n\n"
                             f"Nomi: {blog.title}\n\n"
                             f"{blog.description}\n\n"
                             f"Blog egasi: {blog.owner_name}\n\n"
                             f"Yaratilgan vaqti: {str(blog.created_at)[:-7]}\n\n")


@admin_router.message(F.text == "Foydalanuvchilarni ko'rish")
async def view_users(message: types.Message):
    db = SessionLocal()
    users = db.query(User).all()
    await message.answer("Foydalnuvchilar:", reply_markup=FOYDALANUVCHILAR)
    for user in users:
        blogs = db.query(Blog).filter(Blog.owner_name == user.username).all()
        await message.answer(f"Username: {user.username}\n"
                             f"Full name: {user.first_name} {user.last_name}\n"
                             f"Bloglar soni: {len(blogs)}\n"
                             f"Ro'yhatdan o'tgan vaqti: {user.created_at}")


class DeleteUser(StatesGroup):
    username = State()
    confirmation = State()

    texts = {
        'DeleteUser:username': 'Username ni boshqattan kiriritng',
    }


@admin_router.message(StateFilter(None), F.text == "Foydalanuvchini o'chirish")
async def delete_user(message: types.Message, state: FSMContext):
    await message.answer(
        "Foydalanuvchi usernameni kiriting.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(DeleteUser.username)


@admin_router.message(DeleteUser.username, F.text)
async def get_username(message: types.Message, state: FSMContext):
    db = SessionLocal()
    user = db.query(User).filter(User.username == message.text).first()
    if not user:
        await message.answer("Bunday foydalanuvchi topilmadi. Boshqattan kiriting")
        return
    await state.update_data(username=message.text)
    await message.answer(f"'{message.text}' usernameli foydalanuvchini o'chirishni tasdiqlaysizmi?\n"
                         f"Eslatma: Foydalanuvchi o'chirish bilan birga uning bloglarini ham o'chirsiz",
                         reply_markup=get_keyboard(
                             "Xa ✅",
                             "Bekor qilish",
                             placeholder="Harakatni tanlang",
                             sizes=(2,),
                         ))
    await state.set_state(DeleteUser.confirmation)


@admin_router.message(StateFilter('*'), F.text == "Bekor qilish")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Bekor qilindi", reply_markup=ADMIN_KB)


@admin_router.message(DeleteUser.confirmation, F.text == "Xa ✅")
async def confirm(message: types.Message, state: FSMContext):
    await state.update_data(confirmation=message.text)
    db = SessionLocal()
    data = await state.get_data()
    user = db.query(User).filter(User.username == data['username']).first()
    db.delete(user)
    db.commit()
    await message.answer(f"{data['username']} Foydalanuvchi o'chirildi", reply_markup=FOYDALANUVCHILAR)
    await state.clear()


# Код ниже для машины состояний (FSM)


# class


# class AddProduct(StatesGroup):
#     name = State()
#     description = State()
#     price = State()
#     image = State()
#
#     texts = {
#         'AddProduct:name': 'Введите название заново:',
#         'AddProduct:description': 'Введите описание заново:',
#         'AddProduct:price': 'Введите стоимость заново:',
#         'AddProduct:image': 'Этот стейт последний, поэтому...',
#     }

# Становимся в состояние ожидания ввода name
# @admin_router.message(StateFilter(None), F.text == "Добавить товар")
# async def add_product(message: types.Message, state: FSMContext):
#     await message.answer(
#         "Введите название товара", reply_markup=types.ReplyKeyboardRemove()
#     )
#     await state.set_state(AddProduct.name)


# Хендлер отмены и сброса состояния должен быть всегда именно хдесь,
# после того как только встали в состояние номер 1 (элементарная очередность фильтров)
@admin_router.message(StateFilter('*'), Command("bekorqilish"))
# Вернутся на шаг назад (на прошлое состояние)
@admin_router.message(StateFilter('*'), Command("orqaga"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "Orqaga")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == DeleteUser.username:
        await message.answer("Orqaga yo'l yo'q. Yoki beror qiling yoki username kiriting")
        return

    previous = None
    for step in DeleteUser.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Orqaga qaytarildi \n {DeleteUser.texts[previous.state]}")
            return
        previous = step

# Ловим данные для состояние name и потом меняем состояние на description
# @admin_router.message(AddProduct.name, F.text)
# async def add_name(message: types.Message, state: FSMContext):
#     if len(message.text) >= 100:
#         await message.answer("Название товара не должно превышать 100 символов. \n Введите заново")
#         return
#
#     await state.update_data(name=message.text)
#     await message.answer("Введите описание товара")
#     await state.set_state(AddProduct.description)


# @admin_router.message(AddProduct.name)
# async def add_name2(message: types.Message, state: FSMContext):
#     await message.answer("Вы ввели не допустимые данные, введите текст названия товара")


# Ловим данные для состояние description и потом меняем состояние на price
# @admin_router.message(AddProduct.description, F.text)
# async def add_description(message: types.Message, state: FSMContext):
#     await state.update_data(description=message.text)
#     await message.answer("Введите стоимость товара")
#     await state.set_state(AddProduct.price)

# Хендлер для отлова некорректных вводов для состояния description
# @admin_router.message(AddProduct.description)
# async def add_description2(message: types.Message, state: FSMContext):
#     await message.answer("Вы ввели не допустимые данные, введите текст описания товара")


# Ловим данные для состояние price и потом меняем состояние на image
# @admin_router.message(AddProduct.price, F.text)
# async def add_price(message: types.Message, state: FSMContext):
#     try:
#         float(message.text)
#     except ValueError:
#         await message.answer("Введите корректное значение цены")
#         return
#
#     await state.update_data(price=message.text)
#     await message.answer("Загрузите изображение товара")
#     await state.set_state(AddProduct.image)

# Хендлер для отлова некорректных ввода для состояния price
# @admin_router.message(AddProduct.price)
# async def add_price2(message: types.Message, state: FSMContext):
#     await message.answer("Вы ввели не допустимые данные, введите стоимость товара")


# Ловим данные для состояние image и потом выходим из состояний
# @admin_router.message(AddProduct.image, F.photo)
# async def add_image(message: types.Message, state: FSMContext):
#     await state.update_data(image=message.photo[-1].file_id)
#     await message.answer("Товар добавлен", reply_markup=ADMIN_KB)
#     data = await state.get_data()
#     await message.answer(str(data))
#     await state.clear()

# @admin_router.message(AddProduct.image)
# async def add_image2(message: types.Message, state: FSMContext):
#     await message.answer("Отправьте фото пищи")
