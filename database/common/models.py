import peewee as pw  # type: ignore # для игнорирования проверки mypy

db = pw.SqliteDatabase('nasa_bot_data.db')


class ModelBase(pw.Model):
    """Базовая модель с временем создания записи и информацией о БД."""

    creating_date = pw.DateField()

    class Meta:
        database = db


class Users(ModelBase):
    """Модель пользователей, содержащая идентификатор в Telegram, имя
    пользователя, имя аккаунта, идентификатор чата, в котором пользователь
    запустил бота."""

    id = pw.PrimaryKeyField(null=False)
    username = pw.TextField(null=True)
    first_name = pw.TextField(null=False)
    last_name = pw.TextField(null=True)


class Users2Chats(ModelBase):
    """Модель, содержащая идентификаторы пользователей и чатов, в которых
    они использовали бота."""

    user_id = pw.ForeignKeyField(Users, backref='users2chats')
    chat_id = pw.TextField(null=False)
    unique_id = pw.TextField(null=False)


class Cameras(ModelBase):
    """Модель с акронимами и названиями камер."""

    id = pw.PrimaryKeyField()
    camera = pw.TextField()
    acronym = pw.TextField()


class Rovers(ModelBase):
    """Модель, содержащая название ровера, его последний сол,
    идентификаторы камер."""

    id = pw.PrimaryKeyField()
    name = pw.TextField(null=False)
    last_sol = pw.IntegerField(null=True)
    camera_1 = pw.ForeignKeyField(Cameras, backref='cameras')
    camera_2 = pw.ForeignKeyField(Cameras, backref='cameras')
    camera_3 = pw.ForeignKeyField(Cameras, backref='cameras')


class History(ModelBase):
    """Модель истории запросов."""

    sol = pw.TextField(null=False)
    rover = pw.ForeignKeyField(Rovers, backref='rovers')
    camera_id = pw.ForeignKeyField(Cameras, backref='histories')
    user_id = pw.ForeignKeyField(Users, backref='histories')
