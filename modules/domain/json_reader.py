try:
    import ujson as json
except ImportError:
    import json

import modules.domain.util as util
import random
from modules.constants.morph import R_ANAL
from modules.database.models.replicas import Key


class JsonReader:
    def __init__(self, message, context):
        self.message = message

        self.by_user = [R_ANAL.parse(w)[0].word.lower() for w in self.message.text.split()]
        self.context = [R_ANAL.parse(w)[0].word.lower() for w in context['context'].split()]

    def find_same_percent(self, dict_k):
        expected_user_text = list(map(lambda x: R_ANAL.parse(x)[0].word.lower(), dict_k['by_user'].split()))
        expected_context = list(map(lambda x: R_ANAL.parse(x)[0].word.lower(), dict_k['by_bot'].split()))
        same = int(not bool(expected_context))
        same += sum(int(w in expected_user_text) for w in self.by_user) / (len(self.by_user) if self.by_user else 1)
        same += sum(int(w in expected_context) for w in self.context) / (len(self.context) if self.context else 1)
        return same

    def to_percents(self):
        percent_results = []

        for k in Key.select():
            dict_k = json.loads(k.key)
            util.check_d_keys_for_key(dict_k)
            percent_results.append((k, self.find_same_percent(dict_k)))

        return percent_results

    def __call__(self) -> list[dict]:
        result = []
        for r in json.loads(random.choice(max(self.to_percents(), key=lambda y: y[1])[0].answers).texts_json):
            util.check_d_keys_for_answer(r)
            result.append({
                'type': r['type'],
                'content_json': r['data'],
                'buttons_json': r['buttons'],
            })

        return result
