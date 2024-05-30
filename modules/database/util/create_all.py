from modules.database.models.replicas import Key, Answer
from modules.database.models.requireds import Requires
from modules.database.models.users import TgUser
from modules.database.models.mailing_messages import MailingMessages

from modules.database.database import db


def create_all_database_tables():
    """
    Создает все таблицы в tg_bot_database
    :return:
    """
    with db:
        db.create_tables([
            Requires,
            Key,
            Answer,
            TgUser,
            MailingMessages,
        ])
