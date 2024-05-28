from peewee import CharField, DateTimeField, IntegerField
from modules.database.models.base import BaseModel


class MailingMessages(BaseModel):
    send_data_json = CharField(max_length=4096)
    start_mailing = DateTimeField()
    end_mailing = DateTimeField()
    send_quantity = IntegerField()
    sent_to = IntegerField()
