from aiogram import Bot, Dispatcher, types, executor
import socketio
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import json
from configs import *
from locations import *
import requests

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

    # Отправляем сообщение с ID пользователя
    await message.answer(f"Привет! Ваш ID: {message.from_user.id}")


saved_location = {}


# Функция для обработки местоположения
@dp.message_handler(content_types=types.ContentType.LOCATION)
async def handle_location(message: types.Message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    print(latitude, longitude)

    # Сохраняем местоположение в глобальные переменные
    user_id = message.from_user.id
    saved_location[user_id] = {
        "latitude": latitude,
        "longitude": longitude
    }

    # Отправляем адрес, клавиатуру и вопрос в Telegram
    await bot.send_message(message.chat.id, f"Ваш адрес: {latitude} {longitude}")


@sio.on('message')
async def message(data):
    print("Received data:", data)
    try:
        chat_id = int(data["chat_id"])
        text = data["message"]
        spot_id = data.get("spot_id")
        transaction_id = data.get("transaction_id")
        spot_tablet_id = data.get("spot_tablet_id")
        payed_cash = data.get("payed_cash")
        address = data.get("address")

        keyboard = [
            [InlineKeyboardButton("Доставлено",
                                  callback_data=f'order_close:{spot_id}:{transaction_id}:{spot_tablet_id}:{payed_cash}')],
            [InlineKeyboardButton("Яндекс Карты", url=f"https://yandex.uz/maps/?text={address}")],
            [InlineKeyboardButton("Google Maps", url=f"https://www.google.com/maps/search/?api=1&query={address}")],
            [InlineKeyboardButton("2GIS", url=f"https://2gis.ru/?query={address}")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    except Exception as e:
        print("Error processing message:", e)


async def get_location(chat_id):
    await bot.send_message(chat_id, "Нажми кнопку ниже, чтобы отправить свое местоположение 📍",
                           reply_markup=types.ReplyKeyboardMarkup(
                               keyboard=[
                                   [types.KeyboardButton(text="Отправить местоположение📍", request_location=True)]],
                               resize_keyboard=True
                           ))


@sio.on('text')
async def message(tata):
    print("Received data:", tata)
    try:
        chat_id = int(tata["chat_id"])
        texts = tata["text"]
        await bot.send_message(chat_id=chat_id, text=texts)
        await get_location(chat_id)
    except Exception as e:
        print("Error processing message:", e)


@dp.callback_query_handler(lambda call: 'order_close' in call.data)
async def order_close(callback_query: types.CallbackQuery):
    try:
        # Извлекаем spot_id и transaction_id из данных коллбэка
        data_parts = callback_query.data.split(':')
        spot_id = data_parts[1]
        transaction_id = data_parts[2]
        spot_tablet_id = data_parts[3]
        payed_cash = data_parts[4]

        # URL и данные транзакции
        url = 'https://joinposter.com/api/transactions.closeTransaction'
        params = {
            'token': WEB_TOKEN
        }
        transaction = {
            'spot_id': spot_id,
            'transaction_id': transaction_id,
            'spot_tablet_id': spot_tablet_id,
            'payed_cash': payed_cash
        }

        # Отправка запроса
        response = requests.post(url, params=params, json=transaction)

        # Печать ответа
        print(response.json())

        # Отправляем сообщение о закрытии заказа
        await bot.send_message(chat_id=callback_query.message.chat.id, text="Заказ закрыт успешно.")

    except Exception as e:
        print("Error closing order:", e)

# live_location
@dp.edited_message_handler(content_types=types.ContentType.LOCATION)
async def handle_live_location(message: types.Message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    await bot.send_message(message.chat.id, f"{latitude}    {longitude}")



executor.start_polling(dp, skip_updates=True)
