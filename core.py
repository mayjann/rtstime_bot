from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import configparser


config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

bot = Bot(token=config.get('bot', 'API_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())


# Уведомление о запуске бота.
async def on_startup():
    owner = 2046660433
    await bot.send_message(chat_id=owner, text="Бот запущен")

if __name__ == '__main__':
    from handlers import dp

    executor.start(dp, on_startup())
    executor.start_polling(dp, skip_updates=True)
