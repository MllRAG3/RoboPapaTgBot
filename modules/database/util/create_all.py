from modules.database.models.replicas import Key, Answer
from modules.database.models.requireds import Requires

from modules.database.database import db


def create_all_database_tables():
    with db:
        db.create_tables([
            Requires,
            Key,
            Answer,
        ])
