try:
    import ujson as json
except ImportError:
    import json

from telebot.types import Message

import modules.database.models.users
from modules.constants.tg_bot import BOT
from modules.domain.exxec import Exec
from modules.domain.mailing_sender import MailingSender
from modules.database.util.create_all import create_all_database_tables


@BOT.message_handler(commands=['start'])
def start(message: Message):
    Exec(message).start()


@BOT.message_handler(commands=['photo'])
def for_ads(message: Message):
    try:
        user = modules.database.models.users.TgUser.get(telegram_id=message.from_user.id)
    except AttributeError:
        return
    if not user.is_admin:
        return
    BOT.send_message(message.chat.id, 'Перешли сюда рекламный пост и я расчленю его для бд:')
    BOT.register_next_step_handler(message, callback=to_ads_json)


def to_ads_json(message: Message):
    type = message.content_type
    match type:
        case 'photo':
            send = {'photo': message.photo[0].file_id, 'caption': message.caption, 'parse_mode': 'HTML',
                    'protect_content': int(bool(message.has_protected_content))}
            buttons = message.reply_markup
            if buttons:
                buttons = buttons.to_dict()
        case 'video':
            send = {'video': message.video.file_id, 'caption': message.caption, 'parse_mode': 'HTML',
                    'protect_content': int(bool(message.has_protected_content))}
            buttons = message.reply_markup
            if buttons:
                buttons = buttons.to_dict()
        case _:
            return
    send_json = json.dumps(send, ensure_ascii=False)
    buttons_json = json.dumps(buttons, ensure_ascii=False)
    BOT.send_message(
        message.chat.id,
        text=f'<b>json текста и параметров форматирования:</b>\n<code>{send_json}</code>\n\n'
             f'<b>json кнопок:</b>\n<code>{buttons_json}</code>',
        parse_mode='HTML'
    )


@BOT.message_handler(content_types=['text'])
def send(message: Message):
    MailingSender().send_all()
    Exec(message).send_answer(message)


if __name__ == '__main__':
    create_all_database_tables()
    print('Bot has been started successfully!')
    BOT.infinity_polling()
