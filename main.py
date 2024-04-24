from aiogram import Bot, Dispatcher, types, executor
import socketio
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import json

API_TOKEN = '6175480914:AAHY4t2FMYwJsHhoP4d_yQRpckkAngCfoFo'

WEBSOCKET_URL = 'http://127.0.0.1:5000'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

sio = socketio.AsyncClient()


# Функция для подключения к WebSocket серверу
async def connect_to_socketio():
    try:
        await sio.connect(WEBSOCKET_URL)
        print('Connected to WebSocket server')
    except Exception as e:
        print('Error connecting to WebSocket server:', e)


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Проверяем подключение к WebSocket серверу
    if not sio.connected:
        await connect_to_socketio()

    await message.answer("Привет! Я бот.")

# Ждет message
# @sio.on('message')
# async def message(data):
#     print("Received data:", data)
#     try:
#         # Отправить заказ доставщику
#         await bot.send_message(chat_id=int(data["chat_id"]), text=data["message"])
#     except Exception as e:
#         print("Error processing message:", e)
@sio.on('message')
async def message(data):
    print("Received data:", data)
    try:
        chat_id = int(data["chat_id"])
        text = data["message"]
        keyboard = [
            [InlineKeyboardButton("Яндекс Карты", url="https://yandex.ru/maps")],
            [InlineKeyboardButton("Google Maps", url="https://maps.google.com")],
            [InlineKeyboardButton("2GIS", url="https://2gis.ru")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    except Exception as e:
        print("Error processing message:", e)

executor.start_polling(dp, skip_updates=True)
