from modules.database.models.base import BaseModel
from peewee import IntegerField, DateTimeField, BooleanField
from datetime import datetime


class TgUser(BaseModel):
    telegram_id = IntegerField()
    chat_id = IntegerField()
    is_admin = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    last_activity = DateTimeField(default=datetime.now)
