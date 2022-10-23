from aiogram import types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton


default_buttons = [
    [types.KeyboardButton(text="Ручной счет")],
]

map_button = [
    [types.KeyboardButton("Где я?", request_location=True)]
]



default_keyboard = types.ReplyKeyboardMarkup(
    keyboard=default_buttons,
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Напиши пункт назначения или выбери кнопку"
)

map_keyboard = types.ReplyKeyboardMarkup(
    keyboard=map_button,
    resize_keyboard=True,
    one_time_keyboard=True
)

