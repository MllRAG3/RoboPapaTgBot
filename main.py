try:
    import ujson as json
except ImportError:
    import json

from telebot.types import Message

from modules.database.models.users import TgUser
from modules.constants.tg_bot import BOT
from modules.domain.exxec import Exec, DynamicPicCounter
from modules.domain.to_json import ToJson
from modules.database.util.create_all import create_all_database_tables


@BOT.message_handler(commands=['start'])
def start(message: Message):
    Exec(message).start()
    DynamicPicCounter(message).start_algorythm()


@BOT.message_handler(commands=['dismember'])
def for_ads(message: Message):
    user: TgUser = TgUser.get_or_create(telegram_id=message.from_user.id, chat_id=message.chat.id)[0]
    if not user.is_admin:
        return
    BOT.send_message(message.chat.id, 'Перешли сюда рекламный пост и я расчленю его для бд:')
    tj = ToJson()
    BOT.register_next_step_handler(message, callback=tj)
    while not tj.is_called:
        pass
    BOT.send_message(message.chat.id, str(tj), parse_mode='HTML')


@BOT.callback_query_handler(func=lambda call: call.data == "check_subs")
def check_subs(call):
    Exec(call.message, user=call.from_user).start()


@BOT.message_handler(content_types=['text'])
def send(message: Message):
    Exec(message).send_answer(message)


if __name__ == '__main__':
    create_all_database_tables()
    print('Bot has been started successfully!')
    BOT.infinity_polling()
