from peewee import CharField, IntegerField, ForeignKeyField
from modules.database.models.base import BaseModel


class Users(BaseModel):
    tg_id = IntegerField()
    username = CharField(max_length=32)


class Subscribed(BaseModel):
    user = ForeignKeyField(Users)
    chan_id = IntegerField()
