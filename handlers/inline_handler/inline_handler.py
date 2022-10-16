from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from aiobot import dp, bot
from keyboards import inline_keyboards
import scripts


storage = MemoryStorage()
channel_id = -1001697566553


class Form(StatesGroup):
    name = State()
    nextdst = State()

# кнопка конца работы
@dp.callback_query_handler(lambda c: c.data == 'end_btn')
async def job_end(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await Form.name.set()
    message_to_delete = await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=inline_keyboards.next_kbd,
        text="Напиши следующий пункт назначения или выбери подходящий.")
    async with state.proxy() as data:
        data['msg_del'] = message_to_delete


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    next_dst = message.text
    member = message.from_user.id
    member_name = message.from_user.full_name
    next_id = message.message_id - 1
    await bot.delete_message(chat_id=member, message_id=next_id)
    async with state.proxy() as data:
        data['name'] = message.text
    await Form.next()
    current_date, time_begin_raw, time_end_raw, dst_get = await scripts.end_info.end_info_get(member)
    raw_minutes = await scripts.diff.minutes_make(time_begin_raw, time_end_raw)
    minutes_round = await scripts.diff.minutes_round_make()
    await message.answer(f"""
Информация передана первой линии.

Шаблон времени для ЛУРВ: *{time_begin_raw} {time_end_raw} {minutes_round}*.
Без округления: *{raw_minutes}* минут.
Место проведения работ: *{dst_get}*
Следующее место назначения: *{next_dst}*
Дата проведения работ: *{current_date}*""", parse_mode="Markdown")
    mention = "[" + member_name + "](tg://user?id=" + str(member) + ")"
    await bot.send_message(
        chat_id=channel_id,
        text=f"""
*Инженер* {mention} *закончил работы в {time_end_raw}.*
Шаблон времени для ЛУРВ: *{time_begin_raw} {time_end_raw} {minutes_round}*.
Без округления: *{raw_minutes}* минут.
Место проведения работ: *{dst_get}.*
Следующее место назначения: *{next_dst}.*
Дата проведения работ: *{current_date}*""", parse_mode="Markdown")
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'eat_btn', state=Form.name)
async def eat_begin(callback_query: types.CallbackQuery, state: FSMContext):
    member = callback_query.from_user.id
    member_name = callback_query.from_user.full_name
    await bot.answer_callback_query(callback_query.id)
    await Form.name.set()
    current_date, time_begin_raw, time_end_raw, dst_get = await scripts.end_info.end_info_get(member)
    raw_minutes = await scripts.diff.minutes_make(time_begin_raw, time_end_raw)
    minutes_round = await scripts.diff.minutes_round_make()
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=inline_keyboards.eat_end_kbd,
        text=f"""
Информация передана первой линии.
Приятного аппетита (:

Шаблон времени для ЛУРВ: *{time_begin_raw} {time_end_raw} {minutes_round}*.
Без округления: *{raw_minutes}* минут.
Место проведения работ: *{dst_get}*.
Дата проведения работ: *{current_date}*""", parse_mode="Markdown")
    mention = "[" + member_name + "](tg://user?id=" + str(member) + ")"

    await bot.send_message(
        chat_id=channel_id,
        text=f"""*
Инженер* {mention} *закончил работы в {time_end_raw} и отправился на обед.*
Шаблон времени для ЛУРВ: *{time_begin_raw} {time_end_raw} {minutes_round}*.
Без округления: *{raw_minutes}* минут.
Место проведения работ: *{dst_get}.*
Дата проведения работ: *{current_date}*""", parse_mode="Markdown")
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == 'eat_end_btn')
async def eat_end(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await Form.nextdst.set()
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None)
    eat_message_to_delete = await bot.send_message(
        chat_id=callback_query.from_user.id,
        reply_markup=inline_keyboards.alt_next_kbd,
        text="Напиши следующий пункт назначения или выбери подходящий.")
    async with state.proxy() as data:
        data['eat_msg'] = eat_message_to_delete


@dp.message_handler(state=Form.nextdst)
async def next_dst_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        eat_message_to_delete = data['eat_msg']
    member_id = message.from_user.id
    member_name = message.from_user.full_name
    next_id = eat_message_to_delete.message_id
    await bot.delete_message(chat_id=member_id, message_id=next_id)
    async with state.proxy() as data:
        data['nextdst'] = message.text
    nextdst = message.text
    await message.answer(f"""
Информация передана первой линии.

Следующее место назначения: {nextdst}""")
    await state.finish()
    mention = "[" + member_name + "](tg://user?id=" + str(member_id) + ")"
    bot_msg = f"*Инженер* {mention} *вкусно пообедал.*\nСледующее место назначения: *{nextdst}*."
    await bot.send_message(chat_id=channel_id, text=bot_msg, parse_mode="Markdown")


@dp.callback_query_handler(lambda c: c.data == 'office_btn', state=Form.name)
async def next_dst_office(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    member = callback_query.from_user.id
    member_name = callback_query.from_user.full_name
    await Form.name.set()
    current_date, time_begin_raw, time_end_raw, dst_get = await scripts.end_info.end_info_get(member)
    raw_minutes = await scripts.diff.minutes_make(time_begin_raw, time_end_raw)
    minutes_round = await scripts.diff.minutes_round_make()
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None,
        text=f"""
Информация передана первой линии.

Шаблон времени для ЛУРВ: *{time_begin_raw} {time_end_raw} {minutes_round}*.
Без округления: *{raw_minutes}* минут.
Место проведения работ: *{dst_get}*.
Следующее место назначения: *офис*.
Дата проведения работ: *{current_date}*""", parse_mode="Markdown")
    mention = "[" + member_name + "](tg://user?id=" + str(member) + ")"

    await bot.send_message(
        chat_id=channel_id,
        text=f"""*
Инженер* {mention} *закончил работы в {time_end_raw} и отправился в офис.*
Шаблон времени для ЛУРВ: *{time_begin_raw} {time_end_raw} {minutes_round}*.
Без округления: *{raw_minutes}* минут.
Место проведения работ: *{dst_get}*
Дата проведения работ: *{current_date}*""", parse_mode="Markdown")
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'office_btn', state=Form.nextdst)
async def process_callback_office_btn(callback_query: types.CallbackQuery, state: FSMContext):
    member_name = callback_query.from_user.full_name
    member_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
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
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'home_btn', state=Form.name)
async def next_dst_home(callback_query: types.CallbackQuery, state: FSMContext):
    member_name = callback_query.from_user.full_name
    member_first_name = callback_query.from_user.first_name
    member = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
    await Form.name.set()
    current_date, time_begin_raw, time_end_raw, dst_get = await scripts.end_info.end_info_get(member)
    raw_minutes = await scripts.diff.minutes_make(time_begin_raw, time_end_raw)
    minutes_round = await scripts.diff.minutes_round_make()
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None,
        text=f"""
Информация передана первой линии. Хорошего вечера, {member_first_name}!

Шаблон времени для ЛУРВ: *{time_begin_raw} {time_end_raw} {minutes_round}*.
Без округления: *{raw_minutes}* минут.
Место проведения работ: *{dst_get}*.
Дата проведения работ: *{current_date}*""", parse_mode="Markdown")
    mention = "[" + member_name + "](tg://user?id=" + str(member) + ")"

    await bot.send_message(
        chat_id=channel_id,
        text=f"""*
Инженер* {mention} *закончил работы в {time_end_raw} и отправился домой.*
Шаблон времени для ЛУРВ: *{time_begin_raw} {time_end_raw} {minutes_round}*.
Без округления: *{raw_minutes}* минут.
Место проведения работ: *{dst_get}*
Дата проведения работ: *{current_date}*""", parse_mode="Markdown")
    await state.finish()
