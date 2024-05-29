from peewee import Model, AutoField
from modules.database.database import db


class BaseModel(Model):
    """
    Базовая модель для всех таблиц
    """
    id = AutoField()

    class Meta:
        database = db
