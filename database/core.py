from database.utils.CRUD import CRUDInterface
from database.common.models import db, Users, History, Cameras, Users2Chats, \
    Rovers

db.connect()
db.create_tables([Users, History, Cameras, Users2Chats, Rovers])

crud = CRUDInterface

if __name__ == '__main__':
    crud()
