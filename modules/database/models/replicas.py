from peewee import CharField
from modules.database.models.base import BaseModel


class Replica(BaseModel):
    key = CharField(max_length=255)
    answer = CharField(max_length=4096)
