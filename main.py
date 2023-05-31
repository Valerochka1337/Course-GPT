from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

BOT_TOKEN = '6254843237:AAGQ2PzWCtaYdQsjgRw6s-iyzUTm2d_euhQ'

storage = MemoryStorage()
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    reply_message = "Hello," + message.chat.first_name + "!"
    await bot.send_message(message.chat.id, reply_message)


@dp.message_handler()
async def respond(message: types.Message):
    await message.reply(message.text)


# Start the bots polling loop
if __name__ == '__main__':
    executor.start_polling(dp)
