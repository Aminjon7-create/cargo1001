import logging
import os
import pandas as pd
import asyncio
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# --- ВСТАВЬТЕ СЮДА ВАШ НОВЫЙ ТОКЕН ОТ BOTFATHER ---
BOT_TOKEN = "8622628502:AAFsZpLOoMUX7cp51Tl_fs6-LgVlAIDHMdU"

bot = Bot(token=BOT_TOKEN)
logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

EXCEL_FILES = {
    "🇨🇳 Дар склади Чин": "china.xlsx",
    "🚛 Дар роҳ": "on_the_way.xlsx",
    "🏪 Аз мағозаи 1001": "zafarabad.xlsx",  
    "Супорида шуд": "delivered.xlsx"
}

MENU_BUTTONS = [
    "🔢 Тафтиши трек-код",
    "✅ Склад дар Хитой",
    "📍 Склад дар Тоҷикистон",
    "💲 Нархнома",
    "❌ Молҳои манъшуда",
    "👤 Тамос бо оператор"
]

class TrackStates(StatesGroup):
    waiting_for_track = State()

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
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

@dp.message(F.text == "❌ Молҳои манъшуда")
async def show_banned_items(message: types.Message, state: FSMContext):
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
        "Кӯшиши фармоиш додан ё фиристодани молҳои манъшуда боис ба мусодираи онҳо бидуни бозгашт گردد. "
        "Дар ин ҳолат ширкати **1001 Cargo** ҳеҷ гуна масъулияти молиро ба уҳда намегирад.\n\n"
        "🙏 Хоҳишмандем, ки ин қоидаҳоро дуруст фаҳмед ва тартиби интиқолро риоя намоед!"
    )
    await message.answer(text=banned_text, parse_mode="Markdown")

@dp.message(F.text == "✅ Склад дар Хитой")
async def show_china_warehouse(message: types.Message, state: FSMContext):
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

@dp.message(F.text == "💲 Нархнома")
async def show_price_list(message: types.Message, state: FSMContext):
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

@dp.message(F.text == "🔢 Тафтиши трек-код")
async def ask_track_code(message: types.Message, state: FSMContext):
    await message.answer("📦 Трек-коди бори худро (ё якчанд трек-кодро) барои тафтиш равон кунед!")
    await state.set_state(TrackStates.waiting_for_track)

@dp.message(F.text == "📍 Склад дар Тоҷикистон")
async def show_tajikistan_warehouse(message: types.Message, state: FSMContext):
    photo_path = "1001 photo.jpg"  
    warehouse_text = (
        "📍 **Маълумот дар бораи склади мо дар Тоҷикистон**\n\n"
        "Маркази Зафаробод, мағозаи 1001.\n\n"
        "⏳ **Реҷаи корӣ:** Ҳар рӯз аз 09:00 то 18:00"
    )
    try:
        await message.answer_photo(
            photo=FSInputFile(photo_path),
            caption=warehouse_text,
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Хатогии расм: {e}")
        await message.answer(text=warehouse_text, parse_mode="Markdown")

@dp.message(F.text == "👤 Тамос бо оператор")
async def show_operator_contacts(message: types.Message, state: FSMContext):
    operator_text = (
        "👤 **Тамос бо операторони мо:**\n\n"
        "💬 @aminovrich\n"
        "💬 @aminov_aminjon_77"
    )
    await message.answer(operator_text)

async def process_track_checking(message: types.Message, track_text: str):
    user_tracks = [t.strip() for t in re.split(r'[\s,\n]+', track_text) if t.strip()]
    if not user_tracks:
        return

    loaded_data = {}
    for status_name, file_path in EXCEL_FILES.items():
        try:
            df = pd.read_excel(file_path)
            if 'Track' in df.columns:
                df['Track'] = df['Track'].astype(str).str.strip()
                loaded_data[status_name] = df
        except FileNotFoundError:
            logging.error(f"Файл {file_path} наёфт шуд!")
        except Exception as e:
            logging.error(f"Хатогӣ ҳангоми хондани {file_path}: {e}")

    final_response = "📋 **Натиҷаи тафтиши трек-кодҳои шумо:**\n\n"

    for track in user_tracks:
        found_status = None
        found_date = None
        for status_name, df in loaded_data.items():
            if track in df['Track'].values:
                found_status = status_name
                if 'Date' in df.columns:
                    row = df[df['Track'] == track].iloc[0]
                    found_date = str(row['Date']).strip()
                    if found_date in ["nan", "", "None"]:
                        found_date = None
                break
        
        date_text = f" (📅 Сана: {found_date})" if found_date else ""
        if found_status == "🏪 Аз мағозаи 1001":
            final_response += f"🔹 **{track}**: ✅ Бори шумо омадааст! Метавонед онро омада **аз мағозаи 1001** гиред.{date_text}\n"
        elif found_status is not None:
            final_response += f"🔹 **{track}**: 📌 Статус: **{found_status}**{date_text}\n"
        else:
            final_response += f"🔹 **{track}**: ❌ Маълумот ёфт нашуд (Ҳанӯз ба Чин нарасидааст).\n"

    await message.answer(text=final_response, parse_mode="Markdown")

@dp.message(TrackStates.waiting_for_track)
async def check_track_code_state(message: types.Message, state: FSMContext):
    if message.text in MENU_BUTTONS:
        await state.clear()
        return 
    await process_track_checking(message, message.text)

@dp.message(F.text)
async def catch_any_track_code(message: types.Message):
    if message.text.startswith("/") or message.text in MENU_BUTTONS:
        return
    await process_track_checking(message, message.text)

async def on_startup(bot: Bot) -> None:
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        await bot.set_webhook(f"{RENDER_URL}/webhook")
        logging.info(f"Вебхук успешно установлен на: {RENDER_URL}/webhook")

def main():
    if os.getenv("RENDER") is not None:
        logging.info("Бот запущен на Render в режиме Webhook!")
        dp.startup.register(on_startup)
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_requests_handler.register(app, path="/webhook")
        setup_application(app, dp, bot=bot)
        port = int(os.environ.get("PORT", 8000))
        web.run_app(app, host="0.0.0.0", port=port)
    else:
        logging.info("Бот запущен в режиме Polling!")
        async def run_polling():
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        asyncio.run(run_polling())

if __name__ == "__main__":
    main()
