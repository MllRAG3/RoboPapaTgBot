from peewee import CharField
from modules.database.models.base import BaseModel


class Replica(BaseModel):
    """
    Реплики бота

    Колонки:
    key (str):
      ключ для поиска реплики (до 255 символов, ключевые слова)
    answer (str):
      ответ, который будет отправлен

    Пример:
      ключ: [как дела настроение жизнь поживаешь]

      ответ: [У меня все хорошо! А вы как? Как прошел день?]
    """
    key = CharField(max_length=255)
    answer = CharField(max_length=4096)
