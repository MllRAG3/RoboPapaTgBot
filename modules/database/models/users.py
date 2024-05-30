from modules.database.models.base import BaseModel
from peewee import IntegerField, DateTimeField, BooleanField
from datetime import datetime


class TgUser(BaseModel):
    """
    Пользователи бота (Модель базы данных tg_bot_database)

    Аттрибуты:

    telegram_id (int):
      ID пользователя в Телеграм
    chat_id (int):
      ID чата с пользователем в Телеграм
    is_admin (bool):
      Пользователь имеет права администратора (True если да)
    created_at (datetime):
      Дата и время регистрации пользователя
    last_activity (datetime):
      Дата и время последнего запроса от пользователя к боту
    """
    telegram_id = IntegerField()
    chat_id = IntegerField()
    is_admin = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    last_activity = DateTimeField(default=datetime.now)
