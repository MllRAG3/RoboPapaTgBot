from peewee import Model, AutoField
from modules.database.database import db


class BaseModel(Model):
    id = AutoField()

    class Meta:
        database = db
