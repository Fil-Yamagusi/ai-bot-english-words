#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-
"""2024-02-27 Fil - Future code Yandex.Practicum
AI-Бот, подсказывающий слова из букв другого слова
Описание в README.md

Fil FC AI English words
@fil_fc_ai_ew_bot
https://t.me/fil_fc_ai_ew_bot
7102444889:AAESt-jESjEejW7rC6MLfVcYVoN8I7gc1ek
"""
__version__ = '0.1'
__author__ = 'Firip Yamagusi'

from math import sin, cos, radians
from time import time, strftime
import requests

from transformers import AutoTokenizer
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, Message


# Замените 'YOUR_BOT_TOKEN' на фактический токен вашего бота
TOKEN = '7102444889:AAESt-jESjEejW7rC6MLfVcYVoN8I7gc1ek'
bot_name = "Fil FC AI English words | @fil_fc_ai_ew_bot"
# Для понимания в консоли
print(strftime("%F %T"))
print(bot_name)
print(TOKEN, "\n")

bot = TeleBot(TOKEN)

markup = ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True)
markup.add(* ["more", "break",])

user_data = {}

system_content = ("You are a smart friendly assistant who prompts in "
                  "word games. Answer in common English.")
assistant_content = "Use words that even a child can understand."

model = "mistralai/Mistral-7B-Instruct-v0.2"
max_tokens_in_task = 35


# Токенайзер
def count_tokens(text):
    tokenizer = AutoTokenizer.from_pretrained(model)
    return len(tokenizer.encode(text))


# Часто придётся извиняться за медленный сервер
def send_please_be_patient_message(uid):
    bot.send_message(
        uid, '🙏🏻 <b>This GPT model is very slow, please be patient</b>',
        parse_mode="HTML")


# Проверка наличия записи для данного пользователя
def check_user(uid):
    global user_data
    if uid not in user_data:
        user_data[uid] = {}
        user_data[uid]['task'] = ""
        user_data[uid]['answer'] = ""
        user_data[uid]['busy'] = False


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(m: Message):
    user_id = m.from_user.id
    check_user(user_id)
    bot.send_message(
        user_id,
        '✌🏻 Hello! I am your AI-assistant in <b>word games</b>.\n\n'
        'I usually help to compose new words from the letters of the '
        'original word. You can also ask for help in other similar games.\n\n'
        'Just type your question. For example:\n'
        '<i>Make up words from the letters of the word BEAUTIFUL</i>\nor\n'
        '<i>Name 10 animals with starting letter S</i>',
        parse_mode="HTML")

    # send_please_be_patient_message(user_id)


# Обработчик команды /help
@bot.message_handler(commands=['help'])
def handle_start(m: Message):
    user_id = m.from_user.id
    check_user(user_id)
    bot.send_message(
        user_id,
        '<b>AI-bot for Yandex.Practicum</b>\n\n'
        f'It uses GPT model <i>{model}</i> running on local server.\n'
        f'Use this bot as assistant in word games. It answers much '
        f'faster if you ask in English.\n\n'
        f'Try tasks like these:\n'
        '<i>Tell me 6-letter nouns starting with A and ending with P</i>\nor\n'
        '<i>Give me the longest noun with three vowels</i>\n'
        'etc.',
        parse_mode="HTML")

    # send_please_be_patient_message(user_id)


# Основная обработка входящих запросов
@bot.message_handler(content_types=["text"])
def handle_ask_gpt(m: Message):
    global user_data
    user_id = m.from_user.id
    check_user(user_id)

    if m.text.lower() in ["break"]:
        task = ""
        user_data[user_id]['answer'] = ""
        user_data[user_id]['busy'] = False
        bot.send_message(
            user_id,
            'Something went wrong!\n'
            'Wait for a while and try another task.')
        return

    # Ругаемся, если слишком много токенов в запросе
    try:
        if count_tokens(m.text) > max_tokens_in_task:
            bot.send_message(
                user_id,
                'ℹ️ Your prompt is too long. Please try again.')
            return
    except Exception as e:
        bot.send_message(
            user_id,
            f'❎ Error: {e}')
        return

    # Чтобы не спамил запросами
    if user_data[user_id]['busy']:
        bot.send_message(
            user_id,
            f"❎ Please, don't spam! This task will be ignored.")
        return
    else:
        user_data[user_id]['busy'] = True

    # Если просит продолжить ответ
    task = m.text

    if m.text.lower() in ["more", "continue"]:
        task = user_data[user_id]['answer'] + task
        bot.send_message(
            user_id,
            '...I will continue...')
    else:
        user_data[user_id]['answer'] = ""
        bot.send_message(
            user_id,
            f'New task: <i>{task}</i>',
            parse_mode="HTML")

    # Предупреждаем, что будет долго и отправляем запрос в GPT
    send_please_be_patient_message(user_id)
    resp = requests.post(
        'http://localhost:1234/v1/chat/completions',
        headers={"Content-Type": "application/json"},

        json={
            "messages": [
                {"role": "system",
                 "content": system_content},
                {"role": "user",
                 "content": task},
                {"role": "assistant",
                 "content": assistant_content +
                            user_data[user_id]['answer']},
            ],
            "temperature": 0.8,
            "max_tokens": 50
        }
    )

    if resp.status_code == 200 and 'choices' in resp.json():
        result = resp.json()['choices'][0]['message']['content']
        if result == "":
            bot.send_message(
                user_id,
                'ℹ️ I have said enough.')
        else:
            user_data[user_id]['answer'] += result
            bot.send_message(
                user_id,
                result,
                reply_markup=markup)
            user_data[user_id]['busy'] = False
    else:
        bot.send_message(
            user_id,
            f'GPT is not avaliable now.\n'
            f'Error message: <b>{resp.json()}</b>',
            parse_mode="HTML")


# Запуск бота
bot.infinity_polling()
