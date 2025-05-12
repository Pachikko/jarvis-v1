
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

accounts = ["10k 💰", "25k 💼", "50k 🧳", "100k 🏦", "200k 🚀"]
risks = ["0.3% 🧠", "0.5% 🧩", "1% 📈", "2% 🔥"]
pairs = ["EURUSD 🇪🇺🇺🇸", "GBPUSD 🇬🇧🇺🇸", "EURGBP 🇪🇺🇬🇧", "XAUUSD 🪙", "XAGUSD 🧂"]

user_data = {}

def make_keyboard(options):
    return ReplyKeyboardMarkup(resize_keyboard=True).add(*[KeyboardButton(opt) for opt in options])

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer("Привет, я Jarvis V1 🤖\nВыбери сумму аккаунта:", reply_markup=make_keyboard(accounts))


@dp.message_handler(lambda msg: msg.text in accounts)
async def account_handler(message: types.Message):
    user_data[message.from_user.id]["account"] = int(message.text.split("k")[0]) * 1000
    await message.answer("Теперь выбери риск:", reply_markup=make_keyboard(risks))

@dp.message_handler(lambda msg: msg.text in risks)
async def risk_handler(message: types.Message):
    user_data[message.from_user.id]["risk"] = float(message.text.split("%")[0]) / 100
    await message.answer("Выбери торговую пару:", reply_markup=make_keyboard(pairs))

@dp.message_handler(lambda msg: msg.text in pairs)
async def pair_handler(message: types.Message):
    user_data[message.from_user.id]["pair"] = message.text.split(" ")[0]
    await message.answer("Введи цену входа:")

@dp.message_handler(lambda msg: "entry" not in user_data.get(msg.from_user.id, {}))
async def entry_handler(message: types.Message):
    try:
        user_data[message.from_user.id]["entry"] = float(message.text)
        await message.answer("Теперь введи цену стоп-лосса:")
    except ValueError:
        await message.answer("Пожалуйста, введи корректное число.")

@dp.message_handler(lambda msg: "sl" not in user_data.get(msg.from_user.id, {}))
async def sl_handler(message: types.Message):
    try:
        user_data[message.from_user.id]["sl"] = float(message.text)
        await message.answer("Теперь введи цену тейк-профита:")
    except ValueError:
        await message.answer("Неверный формат SL.")

@dp.message_handler(lambda msg: "tp" not in user_data.get(msg.from_user.id, {}))
async def tp_handler(message: types.Message):
    try:
        user_data[message.from_user.id]["tp"] = float(message.text)
        data = user_data[message.from_user.id]
        risk_amount = data["account"] * data["risk"]
        sl_distance = abs(data["entry"] - data["sl"])
        lot = round(risk_amount / sl_distance / 100 if "XAU" in data["pair"] or "XAG" in data["pair"] else risk_amount / (sl_distance * 10), 2)
        await message.answer(f"🔢 Лот: {lot}\n📉 SL: {data['sl']}\n📈 TP: {data['tp']}\nПара: {data['pair']}", reply_markup=make_keyboard([new_calculation_button.text]))
        user_data.pop(message.from_user.id)
    except Exception:
        await message.answer("Ошибка при расчёте. Проверь входные данные.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
