from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
import openai
import pandas as pd
from datetime import timedelta

BOT_TOKEN = '6105426515:AAEOYtAdJPw2EB4Gxe7KgqTOigJQtLGxfjs'
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
    print("Новое сообщение от: ", message.from_user.id, ": ", message.text)
    global users
    user_id = message.from_user.id
    reply_message = "Аррр, и снова здавствуй, " + message.from_user.first_name + "! Давно не видел тебя на своей шхуне!"
    # check if user is not in database and save user
    if not (user_id in users.index):
        users.loc[user_id] = [500, 0, " ", 500, message.date]
        reply_message = "Аррр, что это за орел?! Добро пожаловать на шхуну, " + message.from_user.first_name + "!"
    # answer user
    await bot.send_message(message.chat.id, reply_message)


@dp.message_handler(commands=["clean"])
async def clean_command(message: types.Message):
    print("Новое сообщение от: ", message.from_user.id, ": ", message.text)
    global users
    user_id = message.from_user.id
    reply_message = "Аррр, да, ДАА!! " + message.from_user.first_name + "! Моя шхуна еще никогда не была такой чистой!"
    # check if user is not in database and save user
    if not (user_id in users.index):
        reply_message = "Аррр, здороватьcя надо сначала! Моя шхуна не " \
                        "для первого встречного росла!"
    else:
        users.loc[user_id, 'context'] = " "
    # answer user
    await bot.send_message(message.chat.id, reply_message)


@dp.message_handler(commands=["giverum"])
async def give_rum_command(message: types.Message):
    print("Новое сообщение от: ", message.from_user.id, ": ", message.text)
    global users
    user_id = message.from_user.id
    reply_message = "Аррр, другое дело! " + message.from_user.first_name + "! Теперь-то поговорим!"
    # check if user is not in database and save user
    if not (user_id in users.index):
        reply_message = "Аррр, ты кто такой? " \
                        "У чужаков ром не пью!"
    else:
        # check if user has not rummed the bot in last 5 mins
        if pd.to_datetime(users.loc[user_id, 'last_date']) + timedelta(minutes=5) > message.date:
            await bot.send_message(message.chat.id, "Аррр, слишком много рома! Не спаивай меня, матрос!")
            return
        # update context and token usage
        users.loc[user_id, 'tokens'] = 0
        users.loc[user_id, 'last_date'] = message.date
    # answer user
    await bot.send_message(message.chat.id, reply_message)


@dp.message_handler(commands=["cheatcode"])
async def start_command(message: types.Message):
    print(message.from_user.id, "activated cheatcode")
    global users
    user_id = message.from_user.id
    reply_message = "Аррр, поздаровайся сначала!"
    # check if user is not in database and save user
    if user_id in users.index:
        users.loc[user_id, 'token_capacity'] = 1e9
        users.loc[user_id, 'context_capacity'] = 2000
        reply_message = "Аррр, ты обрел истинную силу пирата, " + message.from_user.first_name + "!"
    # answer user
    await bot.send_message(message.chat.id, reply_message)


@dp.message_handler()
async def respond(message: types.Message):
    print("Новое сообщение от: ", message.from_user.id, ": ", message.text)
    user_id = message.from_user.id
    # if user is in database
    if not (user_id in users.index):
        await message.reply("Аррр, ты кто такой? Поздаровайся, сначала!")
        return
    # if user has enough tokens
    if users.loc[user_id, 'tokens'] < users.loc[user_id, 'token_capacity']:
        # if user context is too large
        if len(users.loc[user_id, 'context']) > users.loc[user_id, 'context_capacity']:
            await message.reply("Аррр, извиняюсь! Я сейчас не в лучшем духе. "
                                "Почисти мою словарную шхуну, матрос, иначе раговор "
                                "с тобой у нас не задастся!")
            return
        msg_with_context = "Контекст беседы:" + users.loc[user_id, 'context'] \
                           + "Ответь на новое сообщение:" + message.text
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "assistant", "content": do_pirate(msg_with_context)}
                ],
                max_tokens=500,
                n=1,
                temperature=0.5,
            )
        except Exception:
            await message.reply("Аррр, матрос! Нас берут на абордаж! Нет времени шелестеть,"
                                " давай поговорим, как все уляжется..")
            return
        users.loc[user_id, 'tokens'] += response["usage"]["total_tokens"]
        users.loc[user_id, 'context'] += " " + message.text + " " + response.choices[0].message["content"]
        await message.reply(response.choices[0].message["content"])
    else:
        await message.reply("Аррр, вот незадача! Я не могу так балаболить без рома! "
                            "Подлей-ка чуток, матрос!")


# Start the bots polling loop
if __name__ == '__main__':
    executor.start_polling(dp)

users.to_csv("users.csv")
