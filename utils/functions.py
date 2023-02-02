from datetime import datetime
from typing import List

from telebot import types  # type: ignore # для игнорирования проверки mypy

from database.common.models import db, Users, History, Cameras, Users2Chats, \
    Rovers
from database.core import crud

db_write = crud.entry()
db_read = crud.retrieve()


def start_buttons() -> types.ReplyKeyboardMarkup:
    """Возвращает объекты стартовых кнопок меню для выбора ровера или
    истории."""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    rovers = db_read(db, Rovers, Rovers.name)
    for rover in rovers:
        btn = types.KeyboardButton(rover.name)
        markup.add(btn)
    btn = types.KeyboardButton('Последние 10 запросов')
    markup.add(btn)

    return markup


def cams_buttons(rover_name: str) -> types.ReplyKeyboardMarkup:
    """Возвращает объекты кнопок меню для выбора камеры. Принимает название
    ровера."""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    rover = Rovers.get(Rovers.name == rover_name)
    cam_1 = Cameras.get(Cameras.id == rover.camera_1)
    cam_2 = Cameras.get(Cameras.id == rover.camera_2)
    cam_3 = Cameras.get(Cameras.id == rover.camera_3)
    for cam in cam_1, cam_2, cam_3:
        btn = types.KeyboardButton(cam.camera)
        markup.add(btn)

    return markup


def last_sol_button() -> types.ReplyKeyboardMarkup:
    """Возвращает объект кнопки меню для выбора последнего сола."""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('Последний сол')
    markup.add(btn)

    return markup


def db_write_users(message: types.Message) -> None:
    """Принимает сообщение от пользователя. Записывает в информацию о
    пользователе в таблицу Users и информацию о чате пользователя в таблицу
    Users2Chats."""

    uniq = str(message.chat.id) + str(message.from_user.id)

    if not Users.get_or_none(message.from_user.id):
        data = [{'creating_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                 'id': message.from_user.id,
                 'username': message.from_user.username,
                 'first_name': message.from_user.first_name,
                 'last_name': message.from_user.last_name}]
        db_write(db, Users, data)

    if not Users2Chats.get_or_none(Users2Chats.unique_id == uniq):
        data = [{'creating_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                 'user_id': message.from_user.id,
                 'chat_id': message.chat.id,
                 'unique_id': str(message.chat.id) +
                 str(message.from_user.id)}]
        db_write(db, Users2Chats, data)


def db_write_history(message: types.Message, params: List[str]) -> None:
    """Принимает сообщение от пользователя и список с параметрами запроса.
    Записывает информацию о запросе в таблицу History."""

    cam_id = Cameras.get(Cameras.acronym == params[1]).id
    rov_id = Rovers.get(Rovers.name == params[0]).id
    data = [{'creating_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
             'sol': params[2],
             'rover': rov_id,
             'camera_id': cam_id,
             'user_id': message.from_user.id
             }]
    db_write(db, History, data)


def db_select_hist(message: types.Message) -> List[str]:
    """Принимает сообщение от пользователя. Делает запрос к БД, и возвращает
    список с последними десятью запросами пользователя из таблицы History."""

    hist_list = []
    hist = db_read(db, History, History.creating_date, History.sol,
                   Rovers.name, Cameras.camera)\
        .join(Cameras)\
        .switch(History)\
        .join(Rovers)\
        .where(History.user_id == message.from_user.id)\
        .order_by(History.creating_date.desc())
    for row in hist[:10]:
        hist_list.append('Дата и время: {date}\nСол: {sol},\tровер: {rov},'
                         '\tкамера: {cam}\n'.format(
                            date=row.creating_date,
                            sol=row.sol,
                            rov=row.rover.name,
                            cam=row.camera_id.camera.lower()))

    return hist_list


no_messages_to_send = 'В этот сол выбранная камера не делала фото'

start_message_text = 'Я бот, который позволит вам просмотреть \nфото ' \
                     'марсианских роверов Curiosity, Opportunity и Spirit. ' \
                     '\n\nCuriosity - запущен 26 ноября 2011 года для ' \
                     'исследования кратера Гейла на Марсе в рамках миссии ' \
                     'НАСА "Марсианская научная лаборатория". Марсоход ' \
                     'представляет собой автономную химическую лабораторию ' \
                     'в несколько раз больше и тяжелее предыдущих ' \
                     'марсоходов Spirit и Opportunity. Активен.' \
                     '\n\nSpirit - запущен 10 июня 2003 года в рамках ' \
                     'проекта ' \
                     'Mars Exploration Rover. 1 мая 2009 года  «Spirit» ' \
                     'застрял в песчаной дюне. Ровер продолжали ' \
                     'использовать как стационарную платформу. Общение со ' \
                     '«Spirit» прекратилось на 2210-й сол. 24 мая 2011 года ' \
                     'НАСА объявило, что попытки восстановить связь с ' \
                     'ровером не принесли результатов.' \
                     '\n\nOpportunity - марсоход-близнец Spirit. Запущен в ' \
                     'июле 2003 года в рамках проекта Mars Exploration ' \
                     'Rover. 12 июня 2018 года ' \
                     'марсоход перешёл в спящий режим из-за длительной и ' \
                     'мощной пылевой бури, препятствующей поступлению света ' \
                     'на солнечные батареи, с тех пор на связь не выходил. ' \
                     '13 февраля 2019 года NASA официально объявило о ' \
                     'завершении миссии марсохода. Марсоход работал 5111 ' \
                     'солов, вместо запланированных 90.' \
                     '\n\nСол - марсианский день, длится 24 часа 39 минут.' \
                     '\n\nТакже я реагирую на сообщение "Привет" и ' \
                     'отправляю фото дня в 14:00 по Новосибирскому времени.'
