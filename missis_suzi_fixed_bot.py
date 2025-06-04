from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import html
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import asyncio
import logging
import os

from utils import get_order_by_bot_code_or_phone, get_status_text, get_track_text, get_orders, save_review_to_crm
from auth_db import save_user_auth, get_order_id_by_user_id
from keyboards import get_main_keyboard, get_orders_keyboard, get_stars_keyboard

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
PORT = int(os.environ.get("PORT", 3000))

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

class AuthState(StatesGroup):
    waiting_for_code = State()
    waiting_for_review = State()