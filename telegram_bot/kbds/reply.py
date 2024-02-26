from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


# KEYBOARD BUILDER
def get_keyboard(
        *btns: str,
        placeholder: str = None,
        request_contact: int = None,
        request_location: int = None,
        sizes: tuple[int] = (2,),
):
    '''
    Parameters request_contact and request_location must be as indexes of btns args for buttons you need.
    Example:
    get_keyboard(
            "Меню",
            "О магазине",
            "Варианты оплаты",
            "Варианты доставки",
            "Отправить номер телефона",
            placeholder="Что вас интересует?",
            request_contact=4,
            sizes=(2, 2, 1)
        )
    '''
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):

        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder)


# KEYBOARDS
ADMIN_KB = get_keyboard(
    "Foydalanuvchilar",
    "Bloglar",
    "Commentlar",
    placeholder="Harakatni tanlang",
    sizes=(2, 1),
)

FOYDALANUVCHILAR = get_keyboard(
    "Foydalanuvchilarni ko'rish",
    "Foydalanuvchining bloglari",
    "Foydalanuvchini o'chirish",
    "Orqaga",
    placeholder="Harakatni tanlang",
    sizes=(2, 2,),
)

BLOGLAR = get_keyboard(
    "Bloglarni ko'rish",
    "Blogni o'chirish",
    "Orqaga",
    placeholder="Harakatni tanlang",
    sizes=(2, 1,),
)

COMMENTLAR = get_keyboard(
    "Blog commentlarini ko'rish",
    "User commentlarini ko'rish",
    "Blogning hamma commentlarini o'chirish",
    "Userning hamma commentlarini o'chirish",
    "Bitta comment o'chirish",
    "Orqaga",
    placeholder="Harakatni tanlang",
    sizes=(2, 2, 2),
)

TASDIQLASH = get_keyboard(
    "Xa ✅",
    "Bekor qilish",
    placeholder="Harakatni tanlang",
    sizes=(2,),
)
