from peewee import CharField, IntegerField, ForeignKeyField
from modules.database.models.base import BaseModel
from modules.database.models.requireds import Requires


class User(BaseModel):
    tg_id = IntegerField()
    username = CharField(max_length=32)


class Subscribed(BaseModel):
    user = ForeignKeyField(User)
    chan = ForeignKeyField(Requires)
