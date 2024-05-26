from peewee import CharField, ForeignKeyField
from modules.database.models.base import BaseModel


class Key(BaseModel):
    key = CharField(max_length=512)


class Answer(BaseModel):
    key = ForeignKeyField(Key, backref='answers')
    type = CharField(max_length=32)
    main_param = CharField()
    additional_json = CharField(max_length=8192)
