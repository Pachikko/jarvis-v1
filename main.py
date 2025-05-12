import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

accounts = ["10k 💰", "25k 💼", "50k 🧳", "100k 🏦", "200k 🚀"]
risks = ["0.3% 🧠", "0.5% 🧩", "1% 📈", "2% 🔥"]
pairs = ["EURUSD 🇪🇺🇺🇸", "GBPUSD 🇬🇧🇺🇸", "EURGBP 🇪🇺🇬🇧", "XAUUSD 🪙", "XAGUSD 🧂"]

user_data = {}
new_calculation_button = KeyboardButton("Новый расчет 🔄")

def make_keyboard(options, add_back=False):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[KeyboardButton(opt) for opt in options])
    if add_back:
        keyboard.add(new_calculation_button)
    return keyboard

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
    await message.answer(f"Введи цену входа для пары {user_data[message.from_user.id]['pair']}:")

@dp.message_handler(lambda msg: "entry" not in user_data.get(msg.from_user.id, {}))
async def entry_handler(message: types.Message):
    try:
        user_data[message.from_user.id]["entry"] = float(message.text)
        await message.answer("Теперь введи цену стоп-лосса:")
    except ValueError:
        await message.answer("Пожалуйста, введи корректное число. Попробуй еще раз.")

@dp.message_handler(lambda msg: "sl" not in user_data.get(msg.from_user.id, {}))
async def sl_handler(message: types.Message):
    try:
        user_data[message.from_user.id]["sl"] = float(message.text)
        await message.answer("Теперь введи цену тейк-профита:")
    except ValueError:
        await message.answer("Неверный формат SL. Пожалуйста, введи числовое значение.")

@dp.message_handler(lambda msg: "tp" not in user_data.get(msg.from_user.id, {}))
async def tp_handler(message: types.Message):
    try:
        user_data[message.from_user.id]["tp"] = float(message.text)
        data = user_data[message.from_user.id]
        risk_amount = data["account"] * data["risk"]
        sl_distance = abs(data["entry"] - data["sl"])
        if sl_distance == 0:
            await message.answer("Расстояние стоп-лосса равно нулю. Проверьте введенные цены.")
            return
        lot = round(risk_amount / sl_distance / 100 if "XAU" in data["pair"] or "XAG" in data["pair"] else risk_amount / (sl_distance * 10), 2)
        await message.answer(f"🔢 Лот: {lot}\n📉 SL: {data['sl']}\n📈 TP: {data['tp']}\nПара: {data['pair']}", reply_markup=make_keyboard([new_calculation_button.text]))
        del user_data[message.from_user.id]
    except ValueError:
        await message.answer("Некорректный формат цены TP. Пожалуйста, введи числовое значение.")
    except ZeroDivisionError:
        pass # Обработка уже выполнена выше
    except Exception as e:
        print(f"Произошла ошибка при расчете: {e}")
        await message.answer("Произошла ошибка при расчете. Пожалуйста, попробуйте еще раз, начиная с команды /start.")
        if message.from_user.id in user_data:
            del user_data[message.from_user.id]

@dp.message_handler(lambda message: message.text == new_calculation_button.text)
async def new_calculation_handler(message: types.Message):
    await start_handler(message)

async def main():
    await dp.start_polling(dp, bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())
