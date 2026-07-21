import os
import asyncio
import logging
import dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from database import add_user, get_all_books, search_books
dotenv.load_dotenv()

PORT = int(os.getenv("PORT", 8080))

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
# Masalan: https://mening-botim.onrender.com
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"



@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
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
    command_args = message.text.split(maxsplit=1)

    if len(command_args) < 2:
        await message.answer("⚠ Iltimos, qidirmoqchi bo'lgan kitobingiz nomini yozing!\nMisol uchun: `/search Xamsa`",
                             parse_mode=ParseMode.MARKDOWN)
        return
    query_text = command_args[1].strip()
    found_books = search_books(query_text)
    if not found_books:
        await message.answer("Kutubxonamizda bunday kitob topilmadi")
        return
    for book in found_books:
        title = book[0]
        available_copies = book[1]
        if available_copies == 0:
            await message.answer(f"📖 *{title}*\nBu kitob ayni damda qolmagan", parse_mode=ParseMode.MARKDOWN)
        else:
            await message.answer(f"🔍 *Topilgan kitob:* {title}\n📚 *Kutubxonada bor nusxasi:* {available_copies} ta",
                                 parse_mode=ParseMode.MARKDOWN)


@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(
        f"Kechirasiz, men bu buyruqni tushunmadim: '{message.text}'\n"
        f"Iltimos, /books yoki /search buyruqlaridan foydalaning."
    )


async def on_startup(bot: Bot):
    await bot.set_webhook(url=WEBHOOK_URL)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    dp.startup.register(on_startup)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app,dp,port=PORT)
    await web.run_app(app, host="0.0.0.0",port=PORT)


    if __name__ == "__main__":
        asyncio.run(main())
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi!")