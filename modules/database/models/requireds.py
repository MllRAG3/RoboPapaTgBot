from peewee import IntegerField, CharField
from modules.database.models.base import BaseModel


class Requires(BaseModel):
    channel_id = IntegerField()
    note_for_admin = CharField()
