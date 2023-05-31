from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
import openai

BOT_TOKEN = '6254843237:AAGQ2PzWCtaYdQsjgRw6s-iyzUTm2d_euhQ'
OPENAI_TOKEN = "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"

openai.api_key = OPENAI_TOKEN

storage = MemoryStorage()
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)


def do_pirate(input_prompt):
    return input_prompt + f". Ответь, как пират и кратко"


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    reply_message = "Hello, " + message.chat.first_name + "!"
    await bot.send_message(message.chat.id, reply_message)


@dp.message_handler()
async def respond(message: types.Message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "assistant", "content": do_pirate(message.text)}
        ],
        max_tokens=500,
        n=1,
        temperature=0.5,
    )
    await message.reply(response.choices[0].message["content"])


# Start the bots polling loop
if __name__ == '__main__':
    executor.start_polling(dp)
