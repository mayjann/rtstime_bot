from aiogram import types
from core import dp, bot
from aiogram.dispatcher import filters
from keyboards import inline_keyboards
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from datetime import datetime as dt
from keyboards import static_keyboards, inline_keyboards
import configparser
import scripts


config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
channel_id=config.get('bot', 'channel_id')

storage = MemoryStorage()

class Begin(StatesGroup):
    late = State()
    late_dst = State()
    manual_time_first = State()
    manual_time_second = State()


# Регистрируем сообщение с текстом "меню".
@dp.message_handler(text=["Меню", "меню"])
async def menu(message: types.Message):
    # Уведомляем о наличии функций и высылаем inline клавиатуру.
    await message.answer("Пока что можно только узнать геолокацию.", reply_markup=inline_keyboards.map_kbd)


# Регистрируем команду /start
@dp.message_handler(commands="start")
async def manual(message: types.Message):
    
    # Высылаем краткий брифинг о функционале и высылаем клавиатуру.
    await message.answer(f"""
Привет, я твой помощник для расчета времени, для того, чтобы начать, введи имя клиента, к которому приехал.
Еще я умею вручную считать время, для этого нажми на кнопку "Ручной счет" и следуй инструкциям.    
""", reply_markup=static_keyboards.default_keyboard)

# Регистрируем нажатие на кнопку клавиатуры
@dp.message_handler(text="Ручной счет")
async def manual(message: types.Message, state: FSMContext):
    chatid = message.from_user.id
    
    # Запускаем работу машины состояний
    await Begin.manual_time_first.set()
    
    # Высылаем описание и инструкцию использования функции.
    await bot.send_message(
        chat_id=chatid,
        text = """Я могу посчитать время, которое ты мне укажешь.
Я принимаю ответы в формате 12:34.
Напиши мне время, в которое ты начал работу.""")

# Регистрируем первый штамп времени.
@dp.message_handler(state=Begin.manual_time_first)
async def manual_first(message: types.Message, state: FSMContext):
    chatid = message.from_user.id
    manual_first_time_raw = message.text
    
    # Выполняем проверку входящего сообщения на соответствие формату.
    try:
        # Передаем переменную в функцию проверки и получаем результат.
        manual_first_time = await scripts.format_time.format_time(manual_first_time_raw)
        
        # Записываем результат в память
        async with state.proxy() as data:
            data['manual_time_first'] = manual_first_time
        
        # Продолжаем работу машины состояний и высылаем уведомление.
        await Begin.next()
        await bot.send_message(
            chat_id=chatid,
            text = "Отлично, теперь напиши мне время, в которое ты закончил работу.")
    
    # Высылаем уведомление в случае несоответствия входящего сообщения формату.
    except:
        await bot.send_message(
            chat_id=chatid,
            text = "Неправильный формат. Введи в формате 12:34.")


# Регистрируем второй штамп времени.
@dp.message_handler(state=Begin.manual_time_second)
async def process_age_invalid(message: types.Message, state: FSMContext):
    
    # Вытаскиваем первый штамп времени и памяти.
    async with state.proxy() as data:
        manual_first_time = data['manual_time_first']
    chatid = message.from_user.id
    manual_second_time_raw = message.text
    
    # Выполняем проверку входящего сообщения на соответствие формату.
    try:
        
        # Передаем переменную в функцию проверки и получаем результат.
        manual_second_time = await scripts.format_time.format_time(manual_second_time_raw)
        
        # Выполняем калькуляцию затраченного времени.
        raw_minutes = await scripts.diff.minutes_make(manual_first_time, manual_second_time)
        minutes_round = await scripts.diff.minutes_round_make()

        # Высылаем результат калькуляции по запросу и завершаем работу машины состояний.
        await bot.send_message(
            chat_id=chatid,
            text = f"""
Получилось {raw_minutes} минут.
С округлением {minutes_round} минут.""")
        await state.finish()
    
    # Высылаем уведомление в случае несоответствия входящего сообщения формату.
    except:
        await bot.send_message(
            chat_id=chatid,
            text = "Неправильный формат. Введи в формате 12:34.")


# Регистрируем запрос о состоянии бота и высылаем уведомление.
@dp.message_handler(text=["Статус", "статус"])
async def status(message: types.Message):
    await message.answer("Работаю.")


# Принимаем ответ с причиной опоздания.
@dp.message_handler(state=Begin.late)
async def process_name(message: types.Message, state: FSMContext):
    late_reason = message.text
    full_name = message.from_user.full_name
    userid = message.from_user.id
    mention = "[" + full_name + "](tg://user?id=" + str(userid) + ")"
    time_begin_raw = dt.now().strftime("%H:%M")
    datejob = dt.now().strftime("%Y-%m-%d")

    # Вытаскиваем из памяти название объекта.
    async with state.proxy() as data:
        late_dst = data['user_late_dst']

    # Вносим необходимую информацию в базу данных.
    await scripts.mysql.input(full_name, userid, late_dst, time_begin_raw, datejob)
    
    # Уведомляем полевого инженера и центр времени.
    await message.answer(f"Информация передана первой линии.", reply_markup=inline_keyboards.end_kbd)
    await bot.send_message(
        chat_id=channel_id,
        text=f"""
*Инженер* {mention} *прибыл в {late_dst} в {time_begin_raw} с опозданием.*
Причина опоздания: {late_reason}
""", 
        parse_mode="Markdown")
    
    # Завершаем работу машины состояний.
    await state.finish()


# Регистрируем прибытие полевого инженера на объект.
@dp.message_handler()
async def job_begin(message: types.Message, state: FSMContext):

    full_name = message.from_user.full_name
    userid = message.from_user.id
    user_dst = message.text
    time_begin_raw = dt.now().strftime("%H:%M")
    
    # Делаем запрос в базу данных на поиск выполненных визитов полевого инженера на текущий день. 
    datejob = dt.now().strftime("%Y-%m-%d")
    data = await scripts.mysql.output_begin(userid, datejob)
    
    mention = "[" + full_name + "](tg://user?id=" + str(userid) + ")"

    # Выполняем проверку опоздания полевого инженера.
    if data == 0 and time_begin_raw >= str("09:15"):
        
        # Запускаем машину состояний, если опоздание зарегистрировано,
        # вносим название объекта в память и предлагаем написать причину опоздания.
        await Begin.late.set()
        async with state.proxy() as data:
            data['user_late_dst'] = user_dst
        await message.answer("Вижу, что ты опоздал к первому клиенту, напиши почему так вышло.")
    else:

        # Регистрируем прибытие полевого инженера на объект, если опоздание не зарегистрировано
        await scripts.mysql.input(full_name, userid, user_dst, time_begin_raw, datejob)
        await message.answer(f"Информация передана первой линии.", reply_markup=inline_keyboards.end_kbd)
        await bot.send_message(
            chat_id=channel_id, 
            text=f"*Инженер* {mention} *прибыл в {user_dst} в {time_begin_raw}.*",
            parse_mode="Markdown")
        
