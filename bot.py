import os
import asyncio
import logging
import dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode

# database.py modulidan funksiyalarni import qilamiz
from database import add_user, get_all_books, search_books

# .env faylini yuklaymiz
dotenv.load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
logging.basicConfig(level=logging.INFO)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    """/start komandasi yuborilganda foydalanuvchini bazaga qo'shadi"""
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name

    add_user(telegram_id=telegram_id, full_name=full_name)

    welcome_text = (
        f"Assalomu alaykum, {full_name}!\n"
        f"Kutubxona botimizga xush kelibsiz.\n\n"
        f"📚 Quyidagi menyulardan birini tanlang:\n"
        f"1. 📝 Kitoblar ro'yxati = /books\n"
        f"2. 🔍 Qidiruv = /search kitob_nomi"
    )
    await message.answer(welcome_text)


@dp.message(Command("books"))
async def show_books_handler(message: types.Message):
    """/books komandasi yuborilganda umumiy kitoblar ro'yxatini chiqaradi"""
    books = get_all_books()

    if not books:
        await message.answer("❌ Kutubxonada hozircha kitoblar ma'lumotlari mavjud emas.")
        return

    response_text = "📖 **Kutubxonamizdagi kitoblar ro'yxati:**\n\n"

    for index, book in enumerate(books, start=1):
        title = book[0]
        author = book[1]
        copies = book[2]

        response_text += f"{index}. {title} (Muallif: {author}) — Soni: {copies} ta\n"

    await message.answer(response_text, parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("search"))
async def search_books_handler(message: types.Message):
    """5-Topshiriq: /search — Kitob qidirish qismi"""
    # Buyruq yonidagi matnni ajratib olamiz (masalan: /search Xamsa -> Xamsa)
    command_args = message.text.split(maxsplit=1)

    if len(command_args) < 2:
        await message.answer("⚠ Iltimos, qidirmoqchi bo'lgan kitobingiz nomini yozing!\nMisol uchun: `/search Xamsa`",
                             parse_mode=ParseMode.MARKDOWN)
        return

    query_text = command_args[1].strip()

    # Bazadan qidiramiz
    found_books = search_books(query_text)

    # Logika 3: Agar umuman bunday nomli kitob topilmasa
    if not found_books:
        await message.answer("Kutubxonamizda bunday kitob topilmadi")
        return

    # Topilgan kitoblar ro'yxatini tekshiramiz
    for book in found_books:
        title = book[0]
        available_copies = book[1]

        # Logika 2: Agar kitob topilsa, lekin nusxasi qolmagan bo'lsa (available_copies = 0)
        if available_copies == 0:
            await message.answer(f"📖 *{title}*\nBu kitob ayni damda qolmagan", parse_mode=ParseMode.MARKDOWN)

        # Logika 1: Agar kitob topilsa va nusxasi bo'lsa
        else:
            await message.answer(f"🔍 *Topilgan kitob:* {title}\n📚 *Kutubxonada bor nusxasi:* {available_copies} ta",
                                 parse_mode=ParseMode.MARKDOWN)


@dp.message()
async def echo_handler(message: types.Message):
    """Kutilmagan xabarlarni tutib olish uchun handler"""
    await message.answer(
        f"Kechirasiz, men bu buyruqni tushunmadim: '{message.text}'\n"
        f"Iltimos, /books yoki /search buyruqlaridan foydalaning."
    )


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi!")