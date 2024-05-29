from peewee import CharField, BooleanField
from modules.database.models.base import BaseModel


class MailingMessages(BaseModel):
    """
    Таблица с информацией о рассылках
    """
    type = CharField(max_length=16)
    send_data_json = CharField(max_length=4096)
    send_data_buttons_json = CharField(max_length=4096)
    is_active = BooleanField()
