try:
    import ujson as json
except ImportError:
    import json

from telebot.types import Message
import modules.domain.util as util
import random
from modules.constants.morph import R_ANAL
from modules.database.models.replicas import Key


class JsonReader:
    """
    Аттрибуты:

    message (telebot.types.Message):
      вся информация о сеансе с пользователем
    by_user (list[str]):
      Текст сообщения пользователя с приведенными к начальной форме словами и без дубликатов
    context (list[str]):
      Контекст диалога с приведенными к начальной форме словами и без дубликатов
    """
    def __init__(self, message, context):
        self.message: Message = message

        self.by_user: list[str] = list(set([R_ANAL.parse(w)[0].word.lower() for w in self.message.text.split()]))
        self.context: list[str] = list(set([R_ANAL.parse(w)[0].word.lower() for w in context['context'].split()]))

    def find_same_percent(self, dict_k: dict[str, str]) -> int:
        """
        Находит общее совпадение ожидаемого:введенного

        |(expected_user_text:self.by_user)

        |(expected_context:self.context)
        :param dict_k: Словарь с ключом из таблицы Keys
        :return: % Совпадения
        """
        expected_user_text = list(map(lambda x: R_ANAL.parse(x)[0].word.lower(), dict_k['by_user'].split()))
        expected_context = list(map(lambda x: R_ANAL.parse(x)[0].word.lower(), dict_k['by_bot'].split()))
        same = int(not bool(expected_context))
        same += sum(int(w in expected_user_text) for w in self.by_user) / (len(self.by_user) if self.by_user else 1)
        same += sum(int(w in expected_context) for w in self.context) / (len(self.context) if self.context else 1)
        return same*100

    def to_percents(self) -> list[tuple[Key, int]]:
        """
        :return: Список всех ключей с % совпадения
        """
        percent_results = []

        for k in Key.select():
            dict_k = json.loads(k.key)
            util.check_d_keys_for_key(dict_k)
            percent_results.append((k, self.find_same_percent(dict_k)))

        return percent_results

    def __call__(self) -> list[dict]:
        """
        :return: Цепочку ответов, наиболее подходящих под контекст и ввод пользователя
        """
        result = []
        for r in json.loads(random.choice(max(self.to_percents(), key=lambda y: y[1])[0].answers).texts_json):
            util.check_d_keys_for_answer(r)
            result.append({
                'type': r['type'],
                'content_json': r['data'],
                'buttons_json': r['buttons'],
            })

        return result
