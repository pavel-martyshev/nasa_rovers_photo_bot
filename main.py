from typing import List
import subprocess
import sys

import telebot as tb  # type: ignore # для игнорирования проверки mypy
from telebot import types  # type: ignore # для игнорирования проверки mypy
from telebot.apihelper import ApiTelegramException

from database.common.models import Cameras, Rovers
from utils import functions as bot_func
from site_api.core import site_api, url
from tkn import bot_token, api_key

bot = tb.TeleBot(bot_token)
params: List[str] = []

subprocess.Popen([sys.executable, 'send_photo.py'])
# Запуск параллельного скрипта для рассылки фото дня и обновления БД


def hello_message_handler(message: types.Message) -> None:
    """Принимает сообщение от пользователя, отвечает приветственным
    сообщением, записывает данные пользователя в БД, выводит стартовые
    кнопки с роверами и историей."""

    bot_func.db_write_users(message)
    markup = bot_func.start_buttons()
    first_name = message.from_user.first_name
    bot.send_message(message.chat.id, f'Привет, {first_name}',
                     reply_markup=markup)


def select_rover(message: types.Message) -> None:
    """Принимает сообщение от пользователя. Если оно содержит название
    ровера, добавляет его в список params, отправляет сообщение 'Выберите
    камеру', выводит кнопки с камерами."""

    markup = bot_func.cams_buttons(message.text)
    params.append(message.text)
    bot.send_message(message.chat.id, 'Выберите камеру',
                     reply_markup=markup)


def select_camera(message: types.Message) -> None:
    """Принимает сообщение от пользователя. Если оно содержит название
    камеры, добавляет его в список params, отправляет сообщение 'Введите сол
    или выберите последний', выводит кнопку 'Последний сол'."""

    markup = bot_func.last_sol_button()
    params.append(Cameras.get(Cameras.camera == message.text).acronym)
    if str(message.chat.id).startswith('-'):
        bot.send_message(message.chat.id, 'Выберите последний сол или введите '
                                          'свой ответным сообщением',
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Введите сол или выберите последний',
                         reply_markup=markup)


def make_request(message: types.Message) -> None:
    """Принимает сообщение от пользователя. Делает запрос к API. Если
    переменная response не пустая, отправляет в чат фото, название ровера и
    сол. В противном случае отправляет сообщение об отсутствии фото.
    Записывает историю запроса в БД, очищает список params, возвращает
    стартовые кнопки с роверами и историей."""

    markup = bot_func.start_buttons()
    photo_urls = site_api.get_photo_list()
    response = photo_urls('GET', url, api_key, params)

    if len(response) > 0:
        bot.send_media_group(message.chat.id, response[:10])
        bot.send_message(message.chat.id, 'Фото {0}, сол {1}'.format(
                         params[0], params[2]),
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, bot_func.no_messages_to_send,
                         reply_markup=markup)

    bot_func.db_write_history(message, params)
    params.clear()


@bot.message_handler(commands=['start'])
def start_message(message: types.Message) -> None:
    """Обрабатывает команду /start. Принимает сообщение от пользователя.
    Записывает данные пользователя в БД, отправляет стартовое сообщение,
    выводит стартовые кнопки с роверами и историей, очищает список params."""

    bot_func.db_write_users(message)
    markup = bot_func.start_buttons()
    bot.send_message(message.chat.id, bot_func.start_message_text,
                     reply_markup=markup)
    params.clear()


@bot.message_handler(content_types=['text'])
def user_messages_handler(message: types.Message) -> None:
    """Принимает сообщение от пользователя. Записывает информацию о
    пользователе в БД. В зависимости от текста сообщения, вызывает
    соответствующую ему функцию. Добавляет в список params сол, который
    ввел пользователь. Если список params полностью заполнен, вызывает
    функцию для запроса к API."""

    bot_func.db_write_users(message)

    if message.text.lower() == 'привет':
        hello_message_handler(message)

    if Rovers.get_or_none(Rovers.name == message.text):
        select_rover(message)
    elif Cameras.get_or_none(Cameras.camera == message.text):
        select_camera(message)
    elif message.text.isdigit():
        params.append(message.text)
    elif message.text == 'Последний сол':
        sol = Rovers.get(Rovers.name == params[0]).last_sol
        params.append(sol)
    elif message.text == 'Последние 10 запросов':
        hist = bot_func.db_select_hist(message)
        try:
            bot.send_message(message.chat.id, '\n'.join(hist))
        except ApiTelegramException:
            bot.send_message(message.chat.id, 'Ваша история пуста')

    if len(params) == 3:
        make_request(message)


bot.infinity_polling()
