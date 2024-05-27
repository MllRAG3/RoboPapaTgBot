from peewee import CharField, ForeignKeyField
from modules.database.models.base import BaseModel


class Key(BaseModel):
    key = CharField(max_length=512)


class Answer(BaseModel):
    key = ForeignKeyField(Key, backref='answers')
    texts_json = CharField()  # [{"type": ..., "type_value", "kwargs_json": {...}}, ...] - шаблон
