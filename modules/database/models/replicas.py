from peewee import CharField, ForeignKeyField
from modules.database.models.base import BaseModel


class Key(BaseModel):
    """Ключи для доступа к репликам бота (Модель базы данных tg_bot_database)"""
    key = CharField(max_length=512)


class Answer(BaseModel):
    """
    Ответ бота (Модель базы данных tg_bot_database)

    Аттрибуты:

    key (int)
      ID ключа, к которому привязана запись
    texts_json (str)
      JSON-список с ответами (последовательно отправляемыми сообщениями)
    """
    key = ForeignKeyField(Key, backref='answers')
    texts_json = CharField()
