from typing import Final

REQUIRED_D_KEYS_FOR_KEY: Final[set] = {'by_user', 'by_bot'}
REQUIRED_D_KEYS_FOR_ANSWER: Final[set] = {'type', 'type_value', 'kwargs_json'}


def check_d_keys_for_key(dict_):
    if set(dict_.keys()) != REQUIRED_D_KEYS_FOR_KEY:
        raise KeyError(f'Недостаточно ключей!\nНеобходимы: {REQUIRED_D_KEYS_FOR_KEY}\nПолучены: {set(dict_.keys)}')
    return True


def check_d_keys_for_answer(dict_):
    if set(dict_.keys()) != REQUIRED_D_KEYS_FOR_ANSWER:
        raise KeyError(f'Недостаточно ключей!\nНеобходимы: {REQUIRED_D_KEYS_FOR_ANSWER}\nПолучены: {set(dict_.keys)}')
    return True
