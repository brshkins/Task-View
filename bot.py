import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.enums import ParseMode
from datetime import datetime, timedelta
from aiohttp import web
from config import BOT_TOKEN, ADMIN_ID
from db import init_db, add_plan, get_plans_by_date, delete_plans_by_date

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Я бот-планировщик. Введите /week чтобы посмотреть планы.", parse_mode=ParseMode.HTML)


@dp.message(Command("add"))
async def add(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("Недостаточно прав.")

    parts = message.text.split(" ", 2)
    if len(parts) < 3:
        return await message.answer("Формат: /add YYYY-MM-DD текст")

    date_str, task_text = parts[1], parts[2]
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return await message.answer("Неверный формат даты. Используй YYYY-MM-DD.")

    await add_plan(date_str, task_text)
    await message.answer(f"Добавлено на {date_str}:\n{task_text}")


@dp.message(Command("view"))
async def view(message: types.Message):
    parts = message.text.split(" ")
    if len(parts) < 2:
        return await message.answer("Формат: /view YYYY-MM-DD")

    date_str = parts[1]
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return await message.answer("Неверный формат даты. Используй YYYY-MM-DD.")

    tasks = await get_plans_by_date(date_str)
    if tasks:
        text = f"Планы на {date_str}:\n" + "\n".join(f"• {t}" for t in tasks)
    else:
        text = f"На {date_str} пока ничего нет."
    await message.answer(text)


@dp.message(Command("week"))
async def week(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=(datetime.now() + timedelta(days=i)).strftime("%A %d.%m"),
            callback_data=(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        )] for i in range(7)
    ])
    await message.answer("Выбери дату:", reply_markup=keyboard)


@dp.callback_query()
async def handle_date(callback: types.CallbackQuery):
    date_str = callback.data
    tasks = await get_plans_by_date(date_str)
    if tasks:
        text = f"Планы на {date_str}:\n" + "\n".join(f"• {t}" for t in tasks)
    else:
        text = f"На {date_str} пока ничего нет."
    await callback.message.answer(text)
    await callback.answer()


@dp.message(Command("delete"))
async def delete(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("Недостаточно прав.")

    parts = message.text.split(" ")
    if len(parts) < 2:
        return await message.answer("Формат: /delete YYYY-MM-DD")

    date_str = parts[1]
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return await message.answer("Неверный формат даты. Используй YYYY-MM-DD.")

    await delete_plans_by_date(date_str)
    await message.answer(f"Удалены все планы на {date_str}.")


#Обновлённая точка входа
async def main():
    await init_db()
    await dp.start_polling(bot)


# Заглушка для Render
async def handle(request):
    return web.Response(text="Bot is running!")


def run():
    loop = asyncio.get_event_loop()
    loop.create_task(main())  # Бот
    app = web.Application()
    app.router.add_get("/", handle)
    web.run_app(app, port=8080)


if __name__ == "main":
    run()
    print("🟡 Бот запускается...")
    try:
        asyncio.run(main())
    except Exception as e:
        print("🔴 Ошибка при запуске:", e)