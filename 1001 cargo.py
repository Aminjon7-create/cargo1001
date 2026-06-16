import logging
import os
import pandas as pd
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Токен твоего бота
BOT_TOKEN = "8622628502:AAEkDRwCEPBK91g8TRPKcQVBT67aj4DcCmE"

bot = Bot(token=BOT_TOKEN)
logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

# Названия файлов и обновленные статусы (Иваз карда шуд)
EXCEL_FILES = {
    "🇨🇳 Дар склади Чин": "china.xlsx",
    "🚛 Дар роҳ": "on_the_way.xlsx",
    "🏪 Аз мағозаи 1001": "zafarabad.xlsx",  
    "Супорида шуд": "delivered.xlsx"
}

# Состояния для ожидания ввода
class TrackStates(StatesGroup):
    waiting_for_track = State()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    welcome_text = (
        "👋 Бахши лозимаро дар менюи поён интихоб намоед!\n\n"
        "📦 **1001 Cargo** — Барномаро зеркаш кунед ва фармоишҳои "
        "худро дар як клик пайгирӣ намоед."
    )
    
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="🔢 Тафтиши трек-код"),
        types.KeyboardButton(text="✅ Склад дар Хитой"),
        types.KeyboardButton(text="📍 Склад дар Тоҷикистон"),
        types.KeyboardButton(text="💲 Нархнома"),
        types.KeyboardButton(text="❌ Молҳои манъшуда"),
        types.KeyboardButton(text="👤 Тамос бо оператор"),
    )
    builder.adjust(2)
    
    await message.answer(
        text=welcome_text,
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

# --- ОБРАБОТЧИК ДЛЯ КНОПКИ "Молҳои манъшуда" ---
@dp.message(F.text == "❌ Молҳои манъшуда")
async def show_banned_items(message: types.Message):
    banned_text = (
        "🚫 **Рӯйхати молҳои барои интиқол манъшуда тавассути 1001 Cargo**\n\n"
        "Барои таъмини бехатарӣ ва риояи қоидаҳои гумрукӣ, интиқоли ин намуди молҳо қатъиян манъ аст:\n\n"
        "💊 **1. Воситаҳои табобатӣ:** Доруворӣ, ҳабҳо (таблеткаҳо) ва хокаҳо.\n"
        "🗡 **2. Силоҳи сард:** Ҳамаи намудҳои кордҳо, электрошокерҳо, чӯбдастҳо (битаҳо) ва силоҳҳои ба инҳо монанд.\n"
        "💧 **3. Моеъот:** Молҳои зудҳалшаванда ва ҳамаи намудҳои моеъоти гуногун.\n"
        "🔥 **4. Молҳои таркишхавфнок:** Зажигалкаҳо ва баллончаҳои зери фишор (спрейҳо, дезодорантҳо).\n"
        "⚡️ **5. Электроникаи махсус:** Сигорҳои электронӣ (вейпҳо, чилим) ва коптерҳо (дронҳо).\n"
        "🌿 **6. Растаниҳо:** Гулу растаниҳои зинда.\n"
        "🚫 **7. Молҳои категорияи 18+:** Интиқоли ин намуди молҳо қатъиян манъ аст❗️\n\n"
        "⚠️ **Донистани он муҳим аст:**\n"
        "Кӯшиши фармоиш додан ё фиристодани молҳои манъшуда боис ба мусодираи онҳо бидуни бозгашт мегардад. "
        "Дар ин ҳолат ширкати **1001 Cargo** ҳеҷ гуна масъулияти молиро ба уҳда намегирад.\n\n"
        "🙏 Хоҳишмандем, ки ин қоидаҳоро дуруст фаҳмед ва тартиби интиқолро риоя намоед!"
    )
    await message.answer(text=banned_text, parse_mode="Markdown")

# --- ОБРАБОТЧИК ДЛЯ КНОПКИ "Склад дар Хитой" ---
@dp.message(F.text == "✅ Склад дар Хитой")
async def show_china_warehouse(message: types.Message):
    china_photo_path = "china.photo.jpg"  
    china_text = (
        " Zfd1001\n"
        " 17397782303\n"
        " 浙江省金华市义乌市 稠江街道贝村小区23栋三单元拼多多驿站（Zfd1001 - ном ва телефон )"
    )
    await message.answer(text=china_text, parse_mode="Markdown")
    await message.answer(text="Намуна:")
    try:
        await message.answer_photo(photo=FSInputFile(china_photo_path))
    except Exception as e:
        logging.error(f"Хатогии фиристодани расми Чин: {e}")

# --- ОБРАБОТЧИК ДЛЯ КНОПКИ "Нархнома" ---
@dp.message(F.text == "💲 Нархнома")
async def show_price_list(message: types.Message):
    price_text = (
        "💲 **Нархнома :**\n\n"
        "⚖️ Аз **1 кг** то **5 кг** — 26 сомонӣ\n"
        "⚖️ Аз **5 кг** то **30 кг** — 25 сомонӣ\n"
        "⚖️ Аз **30 кг** боло — 23 сомонӣ\n\n"
        "📦 **1 куб** — 2500 сомонӣ\n\n"
        "🎉 **АКСИЯИ КАЛОООН!**\n"
        "📅 **Аз 15.06 то 15.07**\n\n"
        "💰 Нархи **1 кг = 23 сомонӣ**!\n\n"
        "📦 Дар байни ҳамин 30 рӯз, кадом боре ки дар склади Хитой қабул мешавад, бо ҳамин нархи аксионӣ оварда мешавад!\n\n"
        "🤍 *1001 Cargo дар хизмати 😊*"
    )
    await message.answer(text=price_text, parse_mode="Markdown")   

# --- ОБРАБОТЧИК ДЛЯ КНОПКИ "Тафтиши трек-код" ---
@dp.message(F.text == "🔢 Тафтиши трек-код")
async def ask_track_code(message: types.Message, state: FSMContext):
    await message.answer("📦 Трек-коди бори худро барои тафтиш равон кунед!")
    await state.set_state(TrackStates.waiting_for_track)

# --- ОБРАБОТЧИК ДЛЯ КНОПКИ "Склад дар Тоҷикистон" ---
@dp.message(F.text == "📍 Склад дар Тоҷикистон")
async def show_tajikistan_warehouse(message: types.Message):
    photo_path = "1001 photo.jpg"  
    warehouse_text = (
