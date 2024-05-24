from peewee import SqliteDatabase
from typing import Final

db: Final[SqliteDatabase] = SqliteDatabase('tg_bot_database')
