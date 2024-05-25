from peewee import CharField
from modules.database.models.base import BaseModel


class Requires(BaseModel):
    """
    Каналы, на которые необходимо подписаться перед тем, как использовать бота

    Колонки:

    channel_link (str)
      имя канала в формате @sus_channel_name
    """
    channel_link = CharField()
