from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
import openai
import pandas as pd

BOT_TOKEN = '6254843237:AAGQ2PzWCtaYdQsjgRw6s-iyzUTm2d_euhQ'
OPENAI_TOKEN = "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"

openai.api_key = OPENAI_TOKEN

storage = MemoryStorage()
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

users = pd.read_csv("users.csv", index_col=0)


def do_pirate(input_prompt):
    return input_prompt + f". Ответь, как пират и кратко"


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    global users
    user_id = message.from_user.id
    reply_message = "Аррр, и снова здавствуй, " + message.from_user.first_name + "! Давно не видел тебя на своей шхуне!"
    # check if user is not in database and save user
    if not any(users["user_id"] == user_id):
        users.loc[len(users)] = [user_id, 500, 0, "text:", 500]
        reply_message = "Аррр, что это за орел?! Добро пожаловать на шхуну, " + message.from_user.first_name + "!"
    # answer user
    await bot.send_message(message.chat.id, reply_message)


@dp.message_handler(commands=["clean"])
async def clean_command(message: types.Message):
    global users
    user_id = message.from_user.id
    reply_message = "Аррр, да, ДАА!! " + message.from_user.first_name + "! Моя шхуна еще никогда не была такой чистой!"
    # check if user is not in database and save user
    if not any(users["user_id"] == user_id):
        reply_message = "Аррр, здоровать надо сначала! Моя шхуна не " \
                        "для первого встречного росла, " + message.from_user.first_name + "!"
    else:
        # update context and token usage
        users.loc[(users['user_id'] == user_id), 'context'] = ""
    # answer user
    await bot.send_message(message.chat.id, reply_message)


@dp.message_handler(commands=["giverum"])
async def give_rum_command(message: types.Message):
    global users
    user_id = message.from_user.id
    reply_message = "Аррр, другое дело! " + message.from_user.first_name + "! Теперь-то поговорим!"
    # check if user is not in database and save user
    if not any(users["user_id"] == user_id):
        reply_message = "Аррр, здоровать надо сначала! Моя шхуна не " \
                        "для первого встречного росла, " + message.from_user.first_name + "!"
    else:
        # update context and token usage
        users.loc[(users['user_id'] == user_id), 'tokens'] = 0
    # answer user
    await bot.send_message(message.chat.id, reply_message)


@dp.message_handler()
async def respond(message: types.Message):
    user_id = message.from_user.id
    # if user has enough tokens
    if users.loc[(users['user_id'] == user_id), 'tokens'][0] < users.loc[(users['user_id'] == user_id),
                                                                         'token_capacity'][0]:
        # if user context is too large
        if len(users.loc[(users['user_id'] == user_id), 'context'][0]) > users.loc[(users['user_id'] == user_id),
                                                                                   'context_capacity'][0]:
            await message.reply("Аррр, извиняюсь! Я сейчас не в лучшем духе. "
                                "Почисти мою словарную шхуну, матрос, иначе раговор "
                                "с тобой у нас не задастся!")
            return
        msg_with_context = "Контекст беседы:" + users.loc[(users['user_id'] == user_id), 'context'][0] \
                           + "Новое сообщение:" + message.text
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "assistant", "content": do_pirate(msg_with_context)}
            ],
            max_tokens=500,
            n=1,
            temperature=0.5,
        )
        users.loc[(users['user_id'] == user_id), 'tokens'] += response["usage"]["total_tokens"]
        users.loc[(users['user_id'] == user_id), 'context'] += " " \
                                                               + message.text + " " + response.choices[0].message[
                                                                   "content"]
        await message.reply(response.choices[0].message["content"])
    else:
        await message.reply("Аррр, вот незадача! Я не могу так балаболить без рома! "
                            "Подлей-ка чуток, матрос!")


# Start the bots polling loop
if __name__ == '__main__':
    executor.start_polling(dp)

users.to_csv("users.csv")
