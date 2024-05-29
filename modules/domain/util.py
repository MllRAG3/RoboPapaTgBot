from typing import Final
import json

REQUIRED_D_KEYS_FOR_KEY: Final[set] = {'by_user', 'by_bot'}  # {"by_user": "", "by_bot": ""}
REQUIRED_D_KEYS_FOR_ANSWER: Final[set] = {'data', 'buttons', 'type'}  # [{"data": "", "buttons": "", "type": ""}]


def check_d_keys_for_key(dict_):
    if set(dict_.keys()) != REQUIRED_D_KEYS_FOR_KEY:
        raise KeyError(f'Недостаточно ключей!\nНеобходимы: {REQUIRED_D_KEYS_FOR_KEY}\nПолучены: {set(dict_.keys)}')
    return True


def check_d_keys_for_answer(dict_):
    if set(dict_.keys()) != REQUIRED_D_KEYS_FOR_ANSWER:
        raise KeyError(f'Недостаточно ключей!\nНеобходимы: {REQUIRED_D_KEYS_FOR_ANSWER}\nПолучены: {set(dict_.keys)}')
    return True


def extract_buttons(message):
    buttons = message.reply_markup
    if buttons:
        buttons = buttons.to_dict()
    return buttons


def convert_text_message_to_json(text):
    return json.dumps({'text': text}, ensure_ascii=False)


class ToJsonAnswer:
    def __init__(self):
        self.message_seq = []

    def __call__(self, name=''):
        type = input(f"[ToJsonAnswer]({name if name else '-'}) type -> ")
        buttons_json = input(f"[ToJsonAnswer]({name if name else '-'}) buttons_json -> ")
        text_json = input(f"[ToJsonAnswer]({name if name else '-'}) text_json -> ")
        self.message_seq.append({'data': text_json, 'buttons': buttons_json, 'type': type})

    def __str__(self):
        return json.dumps(self.message_seq, ensure_ascii=False)
