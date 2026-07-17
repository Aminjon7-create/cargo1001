import logging
import os
import pandas as pd
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, URLInputFile, FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Токен твоего бота
BOT_TOKEN = "8622628502:AAEBqB1dTZV14jE23Gut8JC9bYxXAZzsDIE"

bot = Bot(token=BOT_TOKEN)
logging.basicConfig(level=logging.INFO)
dp = Dispatcher()

# Названия 4-х файлов и их обновленные статусы
EXCEL_FILES = {
    "Склад дар Чин": "china.xlsx",
    "Дар роҳ": "on_the_way.xlsx",
    "Дар Зафаробод": "zafarabad.xlsx",  
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
        "📦 **1 куб** — 2500 сомонӣ"
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
        await message.answer(warehouse_text, parse_mode="Markdown")

# --- ОБРАБОТЧИК ДЛЯ КНОПКИ "Тамос бо оператор" ---
@dp.message(F.text == "👤 Тамос бо оператор")
async def show_operator_contacts(message: types.Message):
    operator_text = (
        "👤 **Тамос бо операторони мо:**\n\n"
        "💬 @aminovrich\n"
        "💬 @aminov_aminjon_77"
    )
    await message.answer(operator_text)

# --- ЛОГИКАИ ТАФТИШИ ТРЕК-КОД АЗ ФАЙЛҲО ---
@dp.message(TrackStates.waiting_for_track)
async def check_track_code(message: types.Message, state: FSMContext):
    user_track = message.text.strip()
    found_status = None
    found_date = None

    for status_name, file_path in EXCEL_FILES.items():
        try:
            df = pd.read_excel(file_path)
            if 'Track' in df.columns:
                df['Track'] = df['Track'].astype(str)
                if user_track in df['Track'].values:
                    found_status = status_name
                    if 'Date' in df.columns:
                        row = df[df['Track'] == user_track].iloc[0]
                        found_date = str(row['Date']).strip()
                        if found_date == "nan" or found_date == "":
                            found_date = None
                    break 
        except FileNotFoundError:
            logging.error(f"Файл {file_path} наёфт шуд!")
            continue
        except Exception as e:
            logging.error(f"Хатогӣ ҳангоми хондани {file_path}: {e}")
            continue

    date_text = f"\n📅 **Сана:** {found_date}" if found_date else ""

    if found_status == "Дар Зафаробод":
        await message.answer(
            f"✅ Бале, бори шумо бо трек-коди ({user_track}) қабул карда шуд!{date_text}\n"
            f"Шумо метавонед омада онро аз Зафаробод гиред."
        )
    elif found_status is not None:
        await message.answer(
            f"ℹ️ Ҳолати бори шумо бо трек-коди ({user_track}):\n"
            f"📌 **{found_status}**{date_text}"
        )
    else:
        await message.answer(
            f"❌ Маълумот барои трек-коди ({user_track}) ёфт нашуд.\n"
            f"Эҳтимол бор ҳанӯз ба склади мо дар Чин нарасидааст.\n"
            f"Барои дақиқ кардан бо дастгирӣ тамос гиред."
        )
    await state.clear()

# --- УНИВЕРСАЛЬНАЯ ЛОГИКА ЗАПУСКА (И ДЛЯ ПК, И ДЛЯ RENDER) ---
async def on_startup(bot: Bot) -> None:
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        await bot.set_webhook(f"{RENDER_URL}/webhook")
        logging.info(f"Вебхук успешно установлен на: {RENDER_URL}/webhook")

def main():
    # Проверяем, запущен ли код на сервере Render
    if os.getenv("RENDER") is not None:
        logging.info("Бот запущен на Render в режиме Webhook!")
        dp.startup.register(on_startup)
        
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot
        )
        webhook_requests_handler.register(app, path="/webhook")
        setup_application(app, dp, bot=bot)
        
        port = int(os.environ.get("PORT", 8000))
        web.run_app(app, host="0.0.0.0", port=port)
    else:
        logging.info("Бот запущен на домашнем компьютере в режиме Polling!")
        async def run_polling():
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        
        asyncio.run(run_polling())

if __name__ == "__main__":
    main()
