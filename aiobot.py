from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = ''

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

async def on_startup():
    owner = 2046660433
    await bot.send_message(chat_id=owner, text="Бот запущен")

if __name__ == '__main__':
    from handlers import dp

    executor.start(dp, on_startup())
    executor.start_polling(dp, skip_updates=True)
