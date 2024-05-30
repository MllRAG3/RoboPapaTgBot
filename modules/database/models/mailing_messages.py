from peewee import CharField, BooleanField
from modules.database.models.base import BaseModel


class MailingMessages(BaseModel):
    """
    Таблица с информацией о рассылках (Модель базы данных tg_bot_database)

    Аттрибуты:

    type (str):
      Тип сообщения
    send_data_json (str):
      JSON-словарь с данными о сообщении (все кроме кнопок)
    send_data_buttons_json (str):
      JSON-словарь с данными о кнопках (объектах telebot.types.InlineKeyboardMarkup)
    is_active (bool):
      Активная ли запись (True если рассылается)
    """
    type = CharField(max_length=16)
    send_data_json = CharField(max_length=4096)
    send_data_buttons_json = CharField(max_length=4096)
    is_active = BooleanField()
