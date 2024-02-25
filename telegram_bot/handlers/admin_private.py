from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from telegram_bot.filters.chat_types import ChatTypeFilter, IsAdmin
from database import SessionLocal
from models import User, Blog, Tag, Comment
from telegram_bot.kbds.reply import ADMIN_KB, FOYDALANUVCHILAR, BLOGLAR, TASDIQLASH, COMMENTLAR


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message, state: FSMContext):
    await message.answer("Nima qilishni xoxlaysiz?", reply_markup=ADMIN_KB)
    await state.clear()


@admin_router.message(StateFilter("*"), Command('bekorqilish'))
@admin_router.message(StateFilter('*'), F.text == "Bekor qilish")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Bekor qilindi", reply_markup=ADMIN_KB)


@admin_router.message(StateFilter(None), F.text == "Orqaga")
async def admin_orqaga(message: types.Message):
    await message.answer("Nima qilishni xoxlaysiz?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Foydalanuvchilar")
async def users_actions(message: types.Message):
    await message.answer("Harakatni tanlang", reply_markup=FOYDALANUVCHILAR)


@admin_router.message(F.text == "Bloglar")
async def blogs_actions(message: types.Message):
    await message.answer("Harakatni tanlang", reply_markup=BLOGLAR)


@admin_router.message(F.text == "Commentlar")
async def comments_actions(message: types.Message):
    await message.answer("Harakatni tanlang", reply_markup=COMMENTLAR)


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
                             f"Ro'yhatdan o'tgan vaqti: {str(user.created_at)[:-7]}")


@admin_router.message(F.text == "Bloglarni ko'rish")
async def blogs(message: types.Message):
    db = SessionLocal()
    blogs = db.query(Blog).all()
    await message.answer("Bloglar: ", reply_markup=BLOGLAR)
    for blog in blogs:
        tags = db.query(Tag).filter(Tag.blog_id == blog.id).all()
        tags = [tag.name for tag in tags]
        await message.answer(f"Blog ID si: {blog.id}\n\n"
                             f"Nomi: {blog.title}\n\n"
                             f"{blog.description}\n\n"
                             f"Taglar: {', '.join(tags)}\n\n"
                             f"Blog egasi: {blog.owner_name}\n\n"
                             f"Yaratilgan vaqti: {str(blog.created_at)[:-7]}\n\n")


# COMMENT DELETE BY BLOG FSM START
class CommentDeleteByBlog(StatesGroup):
    blog_id = State()
    confirmation = State()


@admin_router.message(StateFilter(None), F.text == "Blogning hamma commentlarini o'chirish")
async def get_blog(message: types.Message, state: FSMContext):
    await message.answer("Blogning IDsini kiriting",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(CommentDeleteByBlog.blog_id)


@admin_router.message(CommentDeleteByBlog.blog_id, F.text)
async def delete_comments(message: types.Message, state: FSMContext):
    db = SessionLocal()
    blog = db.query(Blog).filter(Blog.id == message.text).first()
    if not blog:
        await message.answer("Blog topilmadi. "
                             "Boshqattan kiriting")
        return
    comments = db.query(Comment).filter(Comment.blog_id == message.text).all()
    if not comments:
        await message.answer(f"{blog.id} IDli blogning commentlari topilmadi",
                             reply_markup=COMMENTLAR)
        await state.clear()
        return
    await state.update_data(blog_id=blog.id)
    await state.set_state(CommentDeleteByBlog.confirmation)
    await message.answer(f"{blog.id} IDli blogning {len(comments)} ta "
                         f"commentini o'chirishni tasdiqlaysizmi",
                         reply_markup=TASDIQLASH)


@admin_router.message(CommentDeleteByBlog.confirmation, F.text == "Xa ✅")
async def delete_comments_confirmation(message: types.Message, state: FSMContext):
    db = SessionLocal()
    data = await state.get_data()
    comments = db.query(Comment).filter(Comment.blog_id == data['blog_id']).all()
    for comment in comments:
        db.delete(comment)
        db.commit()
    await state.clear()
    await message.answer("O'chirildi ✅", reply_markup=COMMENTLAR)
# COMMENT DELETE BY BLOG FSM FINISH


# COMMENT VIEW BY BLOG FSM START
class CommentViewByBlog(StatesGroup):
    blog_id = State()


@admin_router.message(StateFilter(None), F.text == "Blog commentlarini ko'rish")
async def comment_view_by_blog(message: types.Message, state: FSMContext):
    await message.answer("Blog IDsini kiriting", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(CommentViewByBlog.blog_id)


@admin_router.message(CommentViewByBlog.blog_id, F.text)
async def comment_view_by_blog(message: types.Message, state: FSMContext):
    db = SessionLocal()
    blog = db.query(Blog).filter(Blog.id == message.text).first()
    if not blog:
        await message.answer("Bunday IDga ega blog mavjud emas. "
                             "Boshqattan kiriting")
        return
    comments = db.query(Comment).filter(Comment.blog_id == message.text).all()
    if not comments:
        await message.answer("Bu blogda commentlar mavjud emas", reply_markup=COMMENTLAR)
        await state.clear()
        return
    await message.answer(f"{blog.id} ID li blog commentlari", reply_markup=COMMENTLAR)
    for comment in comments:
        await message.answer(f"Comment egasi: {comment.username}\n\n"
                             f"{comment.content}\n\n"
                             f"Yozilgan vaqti: {str(comment.created_at)[:-7]}")
    await state.clear()
# COMMENT VIEW BY BLOG FSM FINISH


class CommentViewByUser(StatesGroup):
    username = State()


# COMMENT VIEW BY USER FSM START
@admin_router.message(StateFilter(None), F.text == "User commentlarini ko'rish")
async def get_user_comments(message: types.Message, state: FSMContext):
    await message.answer("Username kiriting",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(CommentViewByUser.username)


@admin_router.message(CommentViewByUser.username, F.text)
async def get_comments(message: types.Message, state: FSMContext):
    db = SessionLocal()
    user = db.query(User).filter(User.username == message.text).first()
    if not user:
        await message.answer("Bunday usernamega ega foydalanuvchi topilmadi. "
                             "Boshqattan kiriting")
        return
    comments = db.query(Comment).filter(Comment.username == message.text).all()
    if not comments:
        await message.answer("Ushbu foydalanuvchining commentlari topilmadi")
        await state.clear()
        return
    await message.answer(f"'{user.username}' usernamega ega foydalanuvchining commentlari:",
                         reply_markup=COMMENTLAR)
    for comment in comments:
        await message.answer(f"Blog_id: {comment.blog_id}\n\n"
                             f"{comment.content}\n\n"
                             f"Yozilgan vaqti: {str(comment.created_at)[:-7]}")
    await state.clear()
# COMMENT VIEW BY USER FSM FINISH


# BLOG VIEW FSM START
class ViewBlogs(StatesGroup):
    username = State()


@admin_router.message(StateFilter(None), F.text == "Foydalanuvchining bloglari")
async def view_blog_by_username(message: types.Message, state: FSMContext):
    await message.answer("Foydalanuvchi usernameni kiriting",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ViewBlogs.username)


@admin_router.message(ViewBlogs.username, F.text)
async def view_blog(message: types.Message, state: FSMContext):
    db = SessionLocal()
    user = db.query(User).filter(User.username == message.text).first()
    if not user:
        await message.answer("Bunday usernamega ega foydalanuvchi topilmadi. "
                             "Qaytadan kiriting")
        return
    await message.answer(f"'{user.username}' username ega foydalanuvchining bloglari:",
                         reply_markup=FOYDALANUVCHILAR)
    blogs = db.query(Blog).filter(Blog.owner_name == message.text).all()
    for blog in blogs:
        tags = db.query(Tag).filter(Tag.blog_id == blog.id).all()
        tags = [tag.name for tag in tags]
        await message.answer(f"Blog IDsi: {blog.id}\n\n"
                             f"Nomi: {blog.title}\n\n"
                             f"{blog.description}\n\n"
                             f"Taglar: {', '.join(tags)}\n\n"
                             f"Yaratilgan vaqti: {str(blog.created_at)[:-7]}")
    await state.clear()
# VIEW BLOG FSM FINISH


# DELETE USER FSM START
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


@admin_router.message(StateFilter(DeleteUser), Command("orqaga"))
@admin_router.message(StateFilter(DeleteUser), F.text == "Orqaga")
async def back_step_user(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == DeleteUser.username:
        await message.answer("Orqaga yo'l yo'q. Yoki beror qiling yoki username kiriting")
        return

    previous = None
    for step in DeleteUser.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Orqaga qaytarildi \n{DeleteUser.texts[previous.state]}")
            return
        previous = step


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
                         reply_markup=TASDIQLASH)
    await state.set_state(DeleteUser.confirmation)


@admin_router.message(DeleteUser.confirmation, F.text == "Xa ✅")
async def confirm_to_delete_user(message: types.Message, state: FSMContext):
    await state.update_data(confirmation=message.text)
    db = SessionLocal()
    data = await state.get_data()
    user = db.query(User).filter(User.username == data['username']).first()
    db.delete(user)
    db.commit()
    await message.answer(f"{data['username']} Foydalanuvchi o'chirildi", reply_markup=FOYDALANUVCHILAR)
    await state.clear()
# USER DELETE FSM FINISH


# BLOG DELETE FSM START
class DeleteBlog(StatesGroup):
    blog_id = State()
    confirmation = State()

    texts = {
        'DeleteBlog:blog_id': 'Blog IDsini boshqattan kiriritng',
    }


@admin_router.message(StateFilter(None), F.text == "Blogni o'chirish")
async def get_blog_id(message: types.Message, state: FSMContext):
    await message.answer("Blog IDsini kiriting",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(DeleteBlog.blog_id)


@admin_router.message(StateFilter(DeleteBlog), Command("orqaga"))
@admin_router.message(StateFilter(DeleteBlog), F.text == "Orqaga")
async def back_step_blog(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == DeleteBlog.blog_id:
        await message.answer("Orqaga yo'l yo'q. Yoki beror qiling yoki blog IDsini kiriting")
        return

    previous = None
    for step in DeleteBlog.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Orqaga qaytarildi \n{DeleteBlog.texts[previous.state]}")
            return
        previous = step


@admin_router.message(DeleteBlog.blog_id, F.text)
async def confirmation_to_delete_blog(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Blog IDsi integer tipda kiritiladi. "
                             "Iltimos boshqattan kiriting")
        return
    db = SessionLocal()
    blog = db.query(Blog).filter(Blog.id == message.text).first()
    if not blog:
        await message.answer("Bunday ID ga ega blog topilmadi. "
                             "Boshqattan kiriting")
        return
    await message.answer(f"Blog ID si: {blog.id}\n\n"
                         f"{blog.description}\n\n"
                         f"Blog egasi: {blog.owner_name}\n\n"
                         f"Blog yaratilgan vaqti: {str(blog.created_at)[:-7]}")
    await state.update_data(blog_id=message.text)
    await message.answer("O'chirishni tasdiqlaysizmi?",
                         reply_markup=TASDIQLASH)
    await state.set_state(DeleteBlog.confirmation)


@admin_router.message(DeleteBlog.confirmation, F.text == "Xa ✅")
async def delete_blog(message: types.Message, state: FSMContext):
    await state.update_data(confirmation=message.text)
    db = SessionLocal()
    data = await state.get_data()
    blog = db.query(Blog).filter(Blog.id == data['blog_id']).first()
    db.delete(blog)
    db.commit()
    await message.answer("O'chirildi ✅", reply_markup=BLOGLAR)
    await state.clear()
# BLOG DELETE FSM FINISH
