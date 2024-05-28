import time
import datetime
try:
    import ujson as json
except ImportError:
    import json

from telebot.types import InlineKeyboardMarkup
from modules.constants.tg_bot import BOT

from modules.database.models.mailing_messages import MailingMessages
from modules.database.models.users import TgUser


class MailingSender:
    @staticmethod
    def send(chat_id: int, type: str, content_json: str, buttons_json: str | None):
        content = json.loads(content_json)
        match type:
            case 'photo':
                BOT.send_photo(chat_id, **content, reply_markup=InlineKeyboardMarkup.de_json(buttons_json))
            case 'video':
                BOT.send_video(chat_id, **content, reply_markup=InlineKeyboardMarkup.de_json(buttons_json))
            case _:
                raise TypeError

    @staticmethod
    def get_ads():
        return MailingMessages.select().where((MailingMessages.send_quantity > 0) & (MailingMessages.send_at < datetime.datetime.now()))

    @staticmethod
    def get_users():
        return TgUser.select()

    def send_all(self):
        for chat_id in map(lambda x: x.chat_id, self.get_users()):
            for ads in self.get_ads():
                if ads.send_quantity <= 0:
                    continue

                try:
                    self.send(
                        chat_id=chat_id,
                        type=ads.type,
                        content_json=ads.send_data_json,
                        buttons_json=ads.send_data_buttons_json if ads.send_data_buttons_json != '{}' else None
                    )
                    ads.send_quantity -= 1
                    ads.send_at = datetime.datetime.now() + datetime.timedelta(days=1)
                    MailingMessages.save(ads)
                except Exception as e:
                    err = e
                    print(err)
                time.sleep(0.5)
