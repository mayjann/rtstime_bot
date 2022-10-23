from aiogram import types
from core import dp, bot
from keyboards import static_keyboards, inline_keyboards
import configparser


config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
channel_id=config.get('bot', 'channel_id')

# Регистрируем сообщение с геолокацией.
@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    
    # Уведомляем о том, что была переслана геолокация.
    await bot.send_message(
        chat_id=channel_id,
        text="Переслана геолокация полевого инженера по запросу.")
    
    # Пересылаем геолокацию в центр времени.
    await bot.forward_message(
            chat_id=channel_id,
            from_chat_id=message.from_user.id,
            message_id=message.message_id)
    
    # Уведомляем полевого инженера о том, что геолокация передана по запросу.
    await bot.send_message(
        chat_id=message.from_user.id,
        reply_markup=static_keyboards.default_keyboard,
        text="Геолокация успешно отправлена.")


# Высылаем список агентов при выборе запроса местоположения в меню.
@dp.callback_query_handler(lambda c: c.data == 'map_btn')
async def map_request(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=inline_keyboards.agents_kbd,
        text="Выбери полевого инженера.")


# Регистрируем команду закрытия меню.
@dp.callback_query_handler(lambda c: c.data == 'cancel_btn')
async def menu_close(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.delete()

# Высылаем запрос о местоположении Виктору.
@dp.callback_query_handler(lambda c: c.data == 'vik_btn')
async def map_notify_vik(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        chat_id=5798284904,
        reply_markup=static_keyboards.map_keyboard,
        text="Виктор, поступил запрос о твоем местоположении, для отправки нажми на кнопку, которая у тебя появилась.")
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None,
        text="Запрос о геолокации отправлен Виктору.")


# Высылаем запрос о местоположении Савелию.
@dp.callback_query_handler(lambda c: c.data == 'sav_btn')
async def map_notify_sav(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        chat_id=5601373435,
        reply_markup=static_keyboards.map_keyboard,
        text="Савелий, поступил запрос о твоем местоположении, для отправки нажми на кнопку, которая у тебя появилась.")
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None,
        text="Запрос о геолокации отправлен Савелию.")
