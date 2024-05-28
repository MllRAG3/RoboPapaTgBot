from peewee import CharField, DateTimeField, IntegerField
from modules.database.models.base import BaseModel


class MailingMessages(BaseModel):
    type = CharField(max_length=16)
    send_data_json = CharField(max_length=4096)
    send_data_buttons_json = CharField(max_length=4096)

    send_at = DateTimeField()
    send_quantity = IntegerField()
