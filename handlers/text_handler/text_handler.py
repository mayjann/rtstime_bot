from aiogram import types
from aiobot import dp, bot
from aiogram.dispatcher import filters
from keyboards import inline_keyboards
from datetime import datetime as dt
import scripts

channel_id = -1001697566553

MANUAL_TIME_PHRASE = [
    'Посчитай'
]

@dp.message_handler(filters.Text(contains=MANUAL_TIME_PHRASE, ignore_case=True))
async def manual(message: types.Message):
    manual_msg = message.text
    command, time_begin_raw, time_end_raw = manual_msg.split()
    raw_minutes = await scripts.diff.minutes_make(time_begin_raw, time_end_raw)
    minutes_round = await scripts.diff.minutes_round_make()

    await message.answer(f"""
Получилось {raw_minutes} минут.
С округлением {minutes_round} минут.""")


@dp.message_handler(text=["Статус", "статус"])
async def status(message: types.Message):
    await message.answer("Работаю.")


@dp.message_handler()
async def job_begin(message: types.Message):
    member_name = message.from_user.full_name
    member = message.from_user.id
    dst = message.text
    mention = "[" + member_name + "](tg://user?id=" + str(member) + ")"
    time_begin_raw = dt.now().strftime("%H:%M")
    await scripts.begin_info.begin_info_get(member, dst)
    await message.answer(f"Информация передана первой линии.", reply_markup=inline_keyboards.end_kbd)
    await bot.send_message(chat_id=channel_id, text=f"*Инженер* {mention} *прибыл в {dst} в {time_begin_raw}.*",
                           parse_mode="Markdown")
