from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from datetime import datetime as dt

from core import dp, bot
from keyboards import inline_keyboards
import configparser
import scripts


config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
channel_id=config.get('bot', 'channel_id')

storage = MemoryStorage()


class Form(StatesGroup):
    name = State()
    nextdst = State()


# Кнопка конца работы.
@dp.callback_query_handler(lambda c: c.data == 'end_btn')
async def job_end(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    # Запускаем машину состояний для ожидания ввода следующего пункта визита полевого инженера.
    await Form.name.set()
    userid = callback_query.from_user.id

    # Отправляем полевому инженеру сообщение с просьбой указать следующий пункт и помечаем его как сообщение,
    # которое надо удалить.
    message_to_delete_raw = await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=inline_keyboards.next_kbd,
        text="Напиши следующий пункт назначения или выбери подходящий.")

    # Получаем идентификатор сообщения и вносим в базу данных.
    message_to_delete = message_to_delete_raw.message_id
    await scripts.mysql.update_msg(userid, message_to_delete)


# Принимаем ответ от полевого инженера.
@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    next_dst = message.text
    userid = message.from_user.id

    # Вытаскиваем из базы данных идентификатор сообщения.
    message_to_delete = scripts.mysql.get_msg(userid)
    time_end_raw = dt.now().strftime("%H:%M")

    # Удаляем предыдущее сообщение и продолжаем работу машины состояний.
    await bot.delete_message(chat_id=userid, message_id=message_to_delete)
    await Form.next()

    # Вносим в базу данных время, в которое полевой инженер закончил работу.
    await scripts.mysql.update(time_end_raw, userid)

    # Вытаскиваем необходимые данные о полевом инженере из базы данных.
    out_name, out_id, out_destination, out_time_begin, out_time_end, out_date = await scripts.mysql.output(userid, time_end_raw)

    # Выполняем калькуляцию затраченного времени.
    raw_minutes = await scripts.diff.minutes_make(out_time_begin, time_end_raw)
    minutes_round = await scripts.diff.minutes_round_make()

    # Отправляем ответ полевому инженеру и уведомление в центр времени.
    await message.answer(f"""
Информация передана первой линии.

Шаблон времени для ЛУРВ: *{out_time_begin} {out_time_end} {minutes_round}*.
Без округления: *{raw_minutes}* минут.
Место проведения работ: *{out_destination}*
Следующее место назначения: *{next_dst}*
Дата проведения работ: *{out_date}*""", parse_mode="Markdown")
    mention = "[" + out_name + "](tg://user?id=" + str(out_id) + ")"
    await bot.send_message(
        chat_id=channel_id,
        text=f"""
*Инженер* {mention} *закончил работы в {out_time_end}.*
Шаблон времени для ЛУРВ: *{out_time_begin} {out_time_end} {minutes_round}*.
Без округления: *{raw_minutes}* минут.
Место проведения работ: *{out_destination}.*
Следующее место назначения: *{next_dst}.*
Дата проведения работ: *{out_date}*""", parse_mode="Markdown")
    
    # Завершаем работу машины состояний.
    await state.finish()


# Принимаем ответ от полевого инженера о том, что он отправился на обед.
@dp.callback_query_handler(lambda c: c.data == 'eat_btn', state=Form.name)
async def eat_begin(callback_query: types.CallbackQuery, state: FSMContext):
    userid = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
    await Form.name.set()
    time_end_raw = dt.now().strftime("%H:%M")

    # Вносим в базу данных время, в которое полевой инженер закончил работу.
    await scripts.mysql.update(time_end_raw, userid)

    # Вытаскиваем необходимые данные о полевом инженере из базы данных.
    out_name, out_id, out_destination, out_time_begin, out_time_end, out_date = await scripts.mysql.output(userid, time_end_raw)

    # Выполняем калькуляцию затраченного времени.
    raw_minutes = await scripts.diff.minutes_make(out_time_begin, out_time_end)
    minutes_round = await scripts.diff.minutes_round_make()

    # Отправляем ответ полевому инженеру и уведомление в центр времени.
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=inline_keyboards.eat_end_kbd,
        text=f"""
Информация передана первой линии.
Приятного аппетита (:

Шаблон времени для ЛУРВ: *{out_time_begin} {out_time_end} {minutes_round}*.
Без округления: *{raw_minutes}* минут.
Место проведения работ: *{out_destination}*.
Дата проведения работ: *{out_date}*""", parse_mode="Markdown")
    mention = "[" + out_name + "](tg://user?id=" + str(out_id) + ")"
    await bot.send_message(
        chat_id=channel_id,
        text=f"""*
Инженер* {mention} *закончил работы в {out_time_end} и отправился на обед.*
Шаблон времени для ЛУРВ: *{out_time_begin} {out_time_end} {minutes_round}*.
Без округления: *{raw_minutes}* минут.
Место проведения работ: *{out_destination}.*
Дата проведения работ: *{out_date}*""", parse_mode="Markdown")
    
    # Завершаем работу машины состояний.
    await state.finish()


# Получаем от полевого инженера ответ о том, что он пообедал.
@dp.callback_query_handler(lambda c: c.data == 'eat_end_btn')
async def eat_end(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    userid = callback_query.from_user.id

    # Запускаем машину состояний для ожидания ввода следующего пункта визита полевого инженера.
    await Form.nextdst.set()

    # Отправляем полевому инженеру сообщение с просьбой указать следующий пункт и помечаем его как сообщение,
    # которое надо удалить.
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None)
    message_to_delete_raw = await bot.send_message(
        chat_id=callback_query.from_user.id,
        reply_markup=inline_keyboards.alt_next_kbd,
        text="Напиши следующий пункт назначения или выбери подходящий.")
    
    # Получаем идентификатор сообщения и вносим в базу данных.
    message_to_delete = message_to_delete_raw.message_id
    await scripts.mysql.update_alt_msg(userid, message_to_delete)


# Принимаем ответ от полевого инженера.
@dp.message_handler(state=Form.nextdst)
async def next_dst_name(message: types.Message, state: FSMContext):
    userid = message.from_user.id
    member_name = message.from_user.full_name
    
    # Вытаскиваем из базы данных идентификатор сообщения.
    date_today = dt.now().strftime("%Y-%m-%d")
    message_to_delete = scripts.mysql.get_alt_msg(userid, date_today)

    # Удаляем предыдущее сообщение и продолжаем работу машины состояний.
    await bot.delete_message(chat_id=userid, message_id=message_to_delete)
    
    nextdst = message.text
    
    # Отправляем ответ полевому инженеру и уведомление в центр времени.
    await message.answer(f"""
Информация передана первой линии.

Следующее место назначения: {nextdst}""")
    mention = "[" + member_name + "](tg://user?id=" + str(userid) + ")"
    bot_msg = f"*Инженер* {mention} *вкусно пообедал.*\nСледующее место назначения: *{nextdst}*."
    await bot.send_message(chat_id=channel_id, text=bot_msg, parse_mode="Markdown")
    
    # Завершаем работу машины состояний.
    await state.finish()


# Получаем от полевого инженера информацию о том, что он отправился в офис.
@dp.callback_query_handler(lambda c: c.data == 'office_btn', state=Form.name)
async def next_dst_office(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    userid = callback_query.from_user.id
    await Form.name.set()
    time_end_raw = dt.now().strftime("%H:%M")
    
    # Вносим в базу данных время, в которое полевой инженер закончил работу.
    await scripts.mysql.update(time_end_raw, userid)
    
    # Вытаскиваем необходимые данные о полевом инженере из базы данных.
    out_name, out_id, out_destination, out_time_begin, out_time_end, out_date = await scripts.mysql.output(userid, time_end_raw)
    
    # Выполняем калькуляцию затраченного времени.
    raw_minutes = await scripts.diff.minutes_make(out_time_begin, time_end_raw)
    minutes_round = await scripts.diff.minutes_round_make()
    
    # Отправляем ответ полевому инженеру и уведомление в центр времени.
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None,
        text=f"""
Информация передана первой линии.

Шаблон времени для ЛУРВ: *{out_time_begin} {out_time_end} {minutes_round}*.
Без округления: *{raw_minutes}* минут.
Место проведения работ: *{out_destination}*.
Следующее место назначения: *офис*.
Дата проведения работ: *{out_date}*""", parse_mode="Markdown")
    mention = "[" + out_name + "](tg://user?id=" + str(out_id) + ")"
    await bot.send_message(
        chat_id=channel_id,
        text=f"""*
Инженер* {mention} *закончил работы в {out_time_end} и отправился в офис.*
Шаблон времени для ЛУРВ: *{out_time_begin} {out_time_end} {minutes_round}*.
Без округления: *{raw_minutes}* минут.
Место проведения работ: *{out_destination}*
Дата проведения работ: *{out_date}*""", parse_mode="Markdown")
    
    # Завершаем работу машины состояний.
    await state.finish()


# Получаем от полевого инженера информацию о том, что он отправился в офис после обеда.
@dp.callback_query_handler(lambda c: c.data == 'office_btn', state=Form.nextdst)
async def process_callback_office_btn(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    member_name = callback_query.from_user.full_name
    member_id = callback_query.from_user.id
    
    # Отправляем ответ полевому инженеру и уведомление в центр времени.
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None,
        text=f"""
Информация передана первой линии.

Следующее место назначения: *офис*.""", parse_mode="Markdown")
    mention = "["+member_name+"](tg://user?id="+str(member_id)+")"
    await bot.send_message(
        chat_id=channel_id,
        text=f"""*
Инженер* {mention} *вкусно пообедал.*
Следующее место назначения: *Офис.*""", parse_mode="Markdown")
    
    # Завершаем работу машины состояний.
    await state.finish()


# Получаем от полевого инженера информацию о том, что он отправился домой.
@dp.callback_query_handler(lambda c: c.data == 'home_btn', state=Form.name)
async def next_dst_home(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    member_first_name = callback_query.from_user.first_name
    userid = callback_query.from_user.id
    await Form.name.set()
    time_end_raw = dt.now().strftime("%H:%M")
    
    # Вносим в базу данных время, в которое полевой инженер закончил работу.
    await scripts.mysql.update(time_end_raw, userid)
    
    # Вытаскиваем необходимые данные о полевом инженере из базы данных.
    out_name, out_id, out_destination, out_time_begin, out_time_end, out_date = await scripts.mysql.output(userid, time_end_raw)
    
    # Выполняем калькуляцию затраченного времени.
    raw_minutes = await scripts.diff.minutes_make(out_time_begin, time_end_raw)
    minutes_round = await scripts.diff.minutes_round_make()
    
    # Отправляем ответ полевому инженеру и уведомление в центр времени.
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None,
        text=f"""
Информация передана первой линии. Хорошего вечера, {member_first_name}!

Шаблон времени для ЛУРВ: *{out_time_begin} {out_time_end} {minutes_round}*.
Без округления: *{raw_minutes}* минут.
Место проведения работ: *{out_destination}*.
Дата проведения работ: *{out_date}*""", parse_mode="Markdown")
    mention = "[" + out_name + "](tg://user?id=" + str(out_id) + ")"
    await bot.send_message(
        chat_id=channel_id,
        text=f"""*
Инженер* {mention} *закончил работы в {out_time_end} и отправился домой.*
Шаблон времени для ЛУРВ: *{out_time_begin} {out_time_end} {minutes_round}*.
Без округления: *{raw_minutes}* минут.
Место проведения работ: *{out_destination}*
Дата проведения работ: *{out_date}*""", parse_mode="Markdown")
    
    # Завершаем работу машины состояний.
    await state.finish()
