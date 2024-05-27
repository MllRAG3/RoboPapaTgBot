from modules.database.models.base import BaseModel
from peewee import IntegerField, DateTimeField
from datetime import datetime


class TgUser(BaseModel):
    telegram_id = IntegerField()
    created_at = DateTimeField(default=datetime.now)
    last_activity = DateTimeField(default=datetime.now)
