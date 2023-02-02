from typing import TypeVar, Dict, List, Any

from peewee import ModelSelect

from database.common.models import ModelBase
from ..common.models import db

T = TypeVar('T')


def _data_entry(database: db, model: T, *data: List[Dict]) -> None:
    """Записывает данные в БД. Принимает базу данных, модель таблицы,
    данные для записи."""

    with database.atomic():
        model.insert_many(*data).execute()


def _data_output(database: db, model: T, *columns: ModelBase) -> ModelSelect:
    """Получает данные из БД. Принимает базу данных, модель таблицы,
    столбцы, которые необходимо получить."""

    with database.atomic():
        response = model.select(*columns)

    return response


def _data_update(database: db, model: T, param: Any) -> None:
    """Обновляет данные в БД. Принимает базу данных, модель таблицы,
    параметры для обновления."""

    with database.atomic():
        model.update(param).execute()


def _data_delete(database: db, model: T, param: Any) -> None:
    """Удаляет данные из БД. Принимает базу данных, модель таблицы,
    параметры для обновления."""

    with database.atomic():
        model.delete().where(param).execute()


class CRUDInterface:
    """Интерфейс для взаимодействия с основным кодом."""

    @staticmethod
    def entry():
        return _data_entry

    @staticmethod
    def retrieve():
        return _data_output

    @staticmethod
    def update():
        return _data_update

    @staticmethod
    def delete():
        return _data_delete


if __name__ == "__main__":
    CRUDInterface()
