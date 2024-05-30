from peewee import IntegerField, CharField
from modules.database.models.base import BaseModel


class Requires(BaseModel):
    """
    Каналы, на которые необходимо подписаться перед тем, как использовать бота
    (Модель базы данных tg_bot_database)

    Аттрибуты:

    channel_link (str)
      ссылка на канал или его имя пользователя (ex: @SusChannelName)
    channel_id (int)
      ID канала
    """
    channel_id = IntegerField()
    channel_link = CharField()
