import json
from datetime import datetime, timedelta
from typing import List, Any

import requests
from telebot import types  # type: ignore # для игнорирования проверки mypy


def _get_correct_url(url: str, params: List[str]) -> str:
    """Возвращает готовый к запросу URL. Принимает URL, параметры для
    обновления."""

    url_sample = url

    return url_sample.format(NUM=params[2], ROVER=params[0], CAM=params[1])


def _make_response(method: str, url: str, success=200) -> Any:
    """Выполняет запрос к API. Принимает метод запроса и URL."""

    response = requests.request(
        method,
        url
    )

    status_code = response.status_code

    if status_code == success:
        return response

    return status_code


def _get_photo_list(method: str, url: str, api_key: str, params: List[str],
                    resp_func=_make_response, url_func=_get_correct_url) \
                    -> List[types.InputMediaPhoto]:
    """Возвращает список ссылок фото. Принимает метод запроса, URL, ключ API,
    параметры для формирования корректного URL, функции для запроса к API и
    формирования корректного URL."""

    url = url_func(url, params)
    url = url + api_key
    response = resp_func(method, url)
    response = json.loads(response.text)
    response = response['photos']
    urls_list = []

    for elem in response:
        urls_list.append(types.InputMediaPhoto(elem['img_src']))

    return urls_list


def _get_curiosity_last_sol(method: str, url: str, api_key: str,
                            resp_func=_make_response) -> str:
    """Возвращает предпоследний сол Curiosity. Принимает метод запроса, URL,
    ключ API, функцию для запроса к API."""

    result = ''
    date_now = datetime.now() - timedelta(2)
    url = url.replace('sol', 'earth_date')
    url = url.replace('&camera={CAM}', '')
    url = url.format(NUM=date_now, ROVER='curiosity') + api_key
    response = resp_func(method, url)
    response = json.loads(response.text)
    response = response['photos']

    for elem in response:
        result = elem['sol']

    return result


def _get_apod(method: str, url: str, api_key: str,
              resp_func=_make_response) -> str:
    """Возвращает API, с данными картинки дня. Принимает метод запроса, URL,
    ключ API, функцию для запроса к API."""

    response = resp_func(method, url + api_key)
    response = json.loads(response.text)

    return response


class SiteApiInterface:
    """Интерфейс для взаимодействия с основным кодом."""

    @staticmethod
    def get_photo_list():
        return _get_photo_list

    @staticmethod
    def get_apod():
        return _get_apod

    @staticmethod
    def get_curiosity_l_sol():
        return _get_curiosity_last_sol


if __name__ == '__main__':
    SiteApiInterface()
