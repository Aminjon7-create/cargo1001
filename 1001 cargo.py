import threading
from http.server import
BaseHTTPRequestHandler, HTTPServer

import logging
import pandas as pd
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# Специальный класс, который отвечает серверу Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def log_message(self, format, *args):
        return  # Отключаем лишние логи в консоли

# Функция для запуска веб-сервера в отдельном потоке
def run_health_check():
    # Render автоматически передает порт в переменную окружения PORT, по умолчанию берем 8000
    import os
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()
# Токен твоего бота, который ты получил у @BotFather
BOT_TOKEN = "8622628502:AAEkDRwCEPBK91g8TRPKcQVBT67aj4DcCmE"

bot = Bot(token=BOT_TOKEN)
logging.basicConfig(level=logging.INFO)
dp = Dispatcher()
# Названия 4-х файлов и их обновленные статусы
EXCEL_FILES = {
    "Склад дар Чин": "china.xlsx",
    "Дар роҳ": "on_the_way.xlsx",
    "Дар Зафаробод": "zafarabad.xlsx",  # Переименовали файл и статус
    "Супорида шуд": "delivered.xlsx"
}
#Состояния для ожидания ввода
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
        types.KeyboardButton(text="🔄 Ворид ба аккаунт"),
        types.KeyboardButton(text="✅ Склад дар Хитой"),
        types.KeyboardButton(text="📍 Склад дар Тоҷикистон"),
        types.KeyboardButton(text="💲 Нархнома"),
        types.KeyboardButton(text="❌ Молҳои манъшуда"),
        types.KeyboardButton(text="🚚 Дархости расонидан"),
        types.KeyboardButton(text="👤 Тамос бо оператор"),
        )
    builder.adjust(2)
    
    await message.answer(
        text=welcome_text,
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

# --- НОВЫЙ ОБРАБОТЧИК ДЛЯ КНОПКИ "Молҳои манъшуда" ---
@dp.message(F.text == "❌ Молҳои манъшуда")
async def show_banned_items(message: types.Message):
    banned_text = (
        "🚫 **Рӯйхати молҳои барои интиқол манъшуда тавассути 1001 Cargo**\n"
        "Барои таъмини бехатарӣ ва риояи қоидаҳои гумрукӣ, интиқоли ин намуди молҳо қатъиян манъ аст:\n\n"
        "🏥 **Тандурустӣ ва тиб**\n"
        "💊 Воситаҳои табобатӣ (доруворӣ): ҳамаи намудҳо (хокаҳо, ҳабҳо/таблеткаҳо, шарбатҳо ва ғайра).\n"
        "💧 Ҳама намуди моеъот: атрҳо (парфюм), хушбӯйкунандаҳо (ароматизаторҳо) ва дигар маводи моеъ.\n\n"
        "⚔️ **Силоҳ ва воситаҳои муҳофизат**\n"
        "🔪 Силоҳи сард: кордҳо, электрошокерҳо, битаҳо (чӯбдастҳо) ва ғайра.\n\n"
        "🚬 **Маҳсулоти тамоку ва кашиданӣ**\n"
        "🚬 Сигорҳои электронӣ: вейпҳо, калјанҳо (чилим) ва қисмҳои эҳтиётии онҳо.\n\n"
        "📦 **Молҳои зудшикан**\n"
        "🪞 Оинаҳо: ва дигар маҳсулоти дорои сатҳи оинавӣ.\n\n"
        "🔌 **Техника ва электроника**\n"
        "📱 Смартфонҳо: ноутбукҳо ва планшетҳо.\n"
        "⌚️ Соатҳо: соатҳои дастӣ (ҳам механикӣ ва ҳам электронӣ).\n"
        "🎧 Гӯшмонакҳо (наушникҳо): ҳамаи намудҳо.\n"
        "📺 Телевизорҳо: ва мониторҳо.\n\n"
        "⚠️ **Донистани он муҳим аст:**\n"
        "Кӯшиши фармоиш додан ё фиристодани молҳои манъшуда боис ба мусодираи онҳо бидуни бозгашт мегардад. "
        "Дар ин ҳолат ширкати **1001 Cargo** ҳеҷ гуна масъулияти молиро ба уҳда намегирад.\n\n"
        "🙏 Хоҳишмандем, ки ин қоидаҳоро дуруст фаҳмед ва тартиби интиқолро риоя намоед!"
    )
# 1. Нажатие на кнопку
@dp.message(F.text == "🔢 Тафтиши трек-код")
async def ask_track_code(message: types.Message, state: FSMContext):
    await message.answer("📦 Трек-коди бори худро барои тафтиш равон кунед!")
    await state.set_state(TrackStates.waiting_for_track)

# 2. Поиск трека и даты по файлам
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
                
                # Ищем строку с трек-кодом
                if user_track in df['Track'].values:
                    found_status = status_name
                    
                    # Проверяем наличие колонки 'Date'
                    if 'Date' in df.columns:
                        row = df[df['Track'] == user_track].iloc[0]
                        found_date = str(row['Date']).strip()
                        
                        if found_date == "nan" or found_date == "":
                            found_date = None
                    
                    break # Нашли — выходим из цикла файлов
                    
        except FileNotFoundError:
            logging.error(f"Файл {file_path} наёфт шуд!")
            continue
        except Exception as e:
            logging.error(f"Хатогӣ ҳангоми хондани {file_path}: {e}")
            continue

    # --- ОТВЕТ ПОЛЬЗОВАТЕЛЮ ---
    
    # Формируем строку с датой, если она заполнена в Excel
    date_text = f"\n📅 **Сана:** {found_date}" if found_date else ""

    # 1. Если товар найден в файле "Дар Зафаробод" (изменили условие)
    if found_status == "Дар Зафаробод":
        await message.answer(
            f"✅ Бале, бори шумо бо трек-коди ({user_track}) қабул карда шуд!{date_text}\n"
            f"Шумо метавонед омада онро аз Зафаробод гиред." # Изменили текст выдачи
        )
        
    # 2. Если товар найден в других файлах (Китай, в пути и т.д.)
    elif found_status is not None:
        await message.answer(
            f"ℹ️ Ҳолати бори шумо бо трек-коди ({user_track}):\n"
            f"📌 **{found_status}**{date_text}"
        )
        
    # 3. Если трек-код вообще не найден
    else:
        await message.answer(
            f"❌ Маълумот барои трек-коди ({user_track}) ёфт нашуд.\n"
            f"Эҳтимол бор ҳанӯз ба склади мо дар Чин нарасидааст.\n"
            f"Барои дақиқ кардан бо дастгирӣ тамос гиред."
        )

    await state.clear()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("Бот бо муваффақият оғоз шуд!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Запускаем веб-сервер в фоне, чтобы Render не ругался
threading.Thread(target=run_health_check, daemon=True).start()
    
    # Дальше идет ваш стандартный запуск бота, например:
    asyncio.run(main())
