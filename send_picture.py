from datetime import datetime

import telebot as tb  # type: ignore # для игнорирования проверки mypy
import schedule
from telebot import types  # type: ignore # для игнорирования проверки mypy
from telebot.apihelper import ApiTelegramException
from googletrans import Translator  # type: ignore

from database.common.models import db, Users2Chats, Rovers, Cameras
from database.core import crud
from site_api.core import site_api, url, apod_url
from tkn import bot_token, api_key

bot = tb.TeleBot(bot_token)

db_read = crud.retrieve()
db_write = crud.entry()
db_update = crud.update()
db_delete = crud.delete()
translator = Translator()

curiosity_last_sol = site_api.get_curiosity_l_sol()
sol = curiosity_last_sol('GET', url, api_key)


def _insert_cameras() -> None:
    """Добавляет данные о камерах в таблицу Cameras при первом запуске бота."""

    if not Cameras.get_or_none(1):
        data = [{'creating_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                 'camera': 'Передняя камера',
                 'acronym': 'fhaz'},
                {'creating_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                 'camera': 'Задняя камера',
                 'acronym': 'rhaz'},
                {'creating_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                 'camera': 'Камера на мачте',
                 'acronym': 'mast'},
                {'creating_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                 'camera': 'Панорамная камера',
                 'acronym': 'pancam'}]
        db_write(db, Cameras, data)


def _insert_rovers() -> None:
    """Добавляет данные о роверах в таблицу Rovers при первом запуске бота."""

    if not Rovers.get_or_none(1):
        data = [{'creating_date': datetime.now().strftime('%Y-%m-%d '
                                                          '%H:%M'),
                 'name': 'Curiosity',
                 'last_sol': sol,
                 'camera_1': 1,
                 'camera_2': 2,
                 'camera_3': 3,
                 },
                {'creating_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                 'name': 'Opportunity',
                 'last_sol': 5111,
                 'camera_1': 1,
                 'camera_2': 2,
                 'camera_3': 4,
                 },
                {'creating_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                 'name': 'Spirit',
                 'last_sol': 2208,
                 'camera_1': 1,
                 'camera_2': 2,
                 'camera_3': 4,
                 }]
        db_write(db, Rovers, data)


def _translate_explanation(explanation: str) -> str:
    """Возвращает переведенный текст с английского на русский. Принимает
    текст для перевода"""

    result = translator.translate(explanation, src='en', dest='ru')

    return result.text


def _send_picture_of_the_day() -> None:
    """Делает запрос к API для получения ссылки на картинку дня. Отправляет
    полученную картинку во все чаты из таблицы Users2Chats. Удаляет запись из
    таблицы Users2Chats, если чат был удален в Telegram"""

    complete_chats = set()
    chats = db_read(db, Users2Chats, Users2Chats.chat_id)
    apod = site_api.get_apod()
    response = apod('GET', apod_url, api_key)
    exp = _translate_explanation(response['explanation'])
    photo_url = response['hdurl']

    for chat in chats:
        if chat.chat_id not in complete_chats:
            try:
                bot.send_photo(chat.chat_id, photo_url)
                bot.send_message(chat.chat_id, exp)
                complete_chats.add(chat.chat_id)
            except ApiTelegramException:
                db_delete(db, Users2Chats, Users2Chats.chat_id == chat.chat_id)


def _update_curiosity_last_sol() -> None:
    """Обновляет столбец last_sol ровера Curiosity."""

    rover = Rovers.update(last_sol=sol).where(Rovers.id == 1)
    rover.execute()


def main() -> None:
    """Отслеживает требуемое время для отправки фото дня и обновления
    последнего сола Curiosity."""

    schedule.every().day.at('14:00').do(_send_picture_of_the_day)
    schedule.every().day.at('00:00').do(_update_curiosity_last_sol)

    while True:
        schedule.run_pending()


if __name__ == '__main__':
    _insert_cameras()
    _insert_rovers()
    main()
