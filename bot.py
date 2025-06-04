import os
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from keyboards import get_main_keyboard, get_orders_keyboard, get_stars_keyboard
from utils import (
    get_order_by_bot_code_or_phone,
    get_status_text,
    get_track_text,
    get_orders,
    save_review_to_crm
)
from auth_db import save_user_auth, get_order_id_by_user_id

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "@Vodyanoy_Dmitriy")
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

class Form(StatesGroup):
    awaiting_bot_code = State()
    awaiting_review_text = State()

async def safe_answer(message: types.Message, text: str, **kwargs):
    try:
        await message.answer(text, **kwargs)
    except Exception as e:
        print(f"❌ Ошибка при отправке сообщения: {e}")

@router.message(F.text == "/start")
async def start_handler(message: types.Message, state: FSMContext):
    existing_order_id = get_order_id_by_user_id(message.from_user.id)
    if existing_order_id:
        await state.update_data(order_id=existing_order_id)
        await safe_answer(message, "👋 Добро пожаловать снова! Вы уже авторизованы.", reply_markup=get_main_keyboard())
    else:
        await state.set_data({"attempts": 0})
        await safe_answer(message, "👋 Привет! Я Missis S’Uzi — ваша заботливая помощница. Введите, пожалуйста, ваш персональный код или номер телефона:")
        await state.set_state(Form.awaiting_bot_code)

@router.message(Form.awaiting_bot_code, F.text)
async def code_handler(message: types.Message, state: FSMContext):
    code_or_phone = message.text.strip()
    data = await state.get_data()
    attempts = data.get("attempts", 0) + 1

    order = get_order_by_bot_code_or_phone(code_or_phone)
    if order:
        order_id = order["id"]
        await state.update_data(order_id=order_id)
        save_user_auth(message.from_user.id, order_id)
        await safe_answer(message, f"✅ Готово! Заказ <b>{order['number']}</b> найден. Выберите, что вас интересует:", reply_markup=get_main_keyboard())
        await state.clear()
    else:
        if attempts < 3:
            await state.update_data(attempts=attempts)
            await safe_answer(message, "❌ Увы, я не нашла заказ по этому коду или номеру телефона. Попробуйте ещё раз — я рядом ❤️")
        else:
            await safe_answer(message, "Очень жаль, что не получается войти 😔 Наверняка есть веская причина, и я обязательно с этим разберусь. Нажмите, пожалуйста, кнопку <b>Помочь</b> — и я сразу начну искать способ Вам помочь 🤍", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="Помочь", callback_data="help")]]))

@router.callback_query(F.data == "help")
async def handle_help(callback: types.CallbackQuery):
    await safe_answer(callback.message, "Спасибо! Я уже занимаюсь вашей ситуацией — всё будет хорошо 🤍")
    try:
        await bot.send_message(ADMIN_USERNAME, f"🆘 Запрос на помощь от пользователя @{callback.from_user.username} (ID: {callback.from_user.id})")
    except Exception as e:
        print(f"Не удалось отправить сообщение администратору: {e}")

@router.callback_query(F.data == "status")
async def status_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = get_status_text(data.get("order_id"))
    await safe_answer(callback.message, text)

@router.callback_query(F.data == "track")
async def track_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = get_track_text(data.get("order_id"))
    await safe_answer(callback.message, text)

@router.callback_query(F.data == "orders")
async def orders_menu(callback: types.CallbackQuery):
    await safe_answer(callback.message, "📦 Выберите, какие заказы показать:", reply_markup=get_orders_keyboard())

@router.callback_query(F.data == "orders_active")
async def active_orders(callback: types.CallbackQuery):
    text = get_orders(active=True)
    await safe_answer(callback.message, text)

@router.callback_query(F.data == "orders_past")
async def past_orders(callback: types.CallbackQuery):
    text = get_orders(active=False)
    await safe_answer(callback.message, text)

@router.callback_query(F.data == "rate")
async def rate_order(callback: types.CallbackQuery):
    await safe_answer(callback.message, "Как бы вы оценили наш сервис по 5-звёздочной шкале?", reply_markup=get_stars_keyboard())

@router.callback_query(F.data.in_(["⭐1", "⭐2", "⭐3", "⭐4", "⭐5"]))
async def handle_rating(callback: types.CallbackQuery, state: FSMContext):
    rating = callback.data[-1]
    await safe_answer(callback.message, f"Спасибо за вашу оценку: {rating} ⭐️ Пожалуйста, напишите пару слов о вашем опыте — это правда важно для <b>меня</b>. Я всё читаю сама, каждое слово 💌")
    await state.set_state(Form.awaiting_review_text)

@router.message(Form.awaiting_review_text, F.text)
async def handle_review(message: types.Message, state: FSMContext):
    data = await state.get_data()
    save_review_to_crm(data.get("order_id"), message.text)
    await safe_answer(message, "Спасибо! Я всё обязательно прочту и учту — ваше мнение помогает мне расти и становиться лучше 💌")
    await state.clear()

@router.callback_query(F.data == "support")
async def support_handler(callback: types.CallbackQuery):
    await safe_answer(callback.message, "Если вдруг что-то пошло не так, я рядом 🤗 Расскажите, пожалуйста, что случилось — я уже готовлю помощь ✨")
    try:
        await bot.send_message(ADMIN_USERNAME, f"📥 Запрос от @{callback.from_user.username} ({callback.from_user.id})")
    except:
        pass

dp.include_router(router)

app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
setup_application(app, dp, bot=bot)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))