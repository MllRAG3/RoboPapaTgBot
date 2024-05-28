import util

try:
    import ujson as json
except ImportError:
    import json

from telebot.types import Message
from typing import Callable


class ToJson:
    def __init__(self):
        self.TYPES: dict[str | Callable] = {
            'photo': self.photo_message_to_dict,
            'video': self.video_message_to_dict,
            'video_note': self.video_note_to_dict,
            'contact': self.contact_to_dict,
            'text': self.text_to_dict,
            'sticker': self.sticker_to_dict,
            'dice': self.dice_to_dict,
            'voice': self.voice_to_dict,
            'document': self.document_to_dict,
        }
        self.jsons: tuple[str, str] = ('null', 'null')
        self.is_called: bool = False

    @staticmethod
    def photo_message_to_dict(message: Message) -> tuple[dict, dict | None]:
        data = {
            'photo': message.photo[0].file_id,
            'caption': message.caption,
            'parse_mode': 'HTML',
        }

        return data, util.extract_buttons(message)

    @staticmethod
    def video_message_to_dict(message: Message) -> tuple[dict, dict | None]:
        data = {
            'video': message.video.file_id,
            'caption': message.caption,
            'parse_mode': 'HTML',
        }

        return data, util.extract_buttons(message)

    @staticmethod
    def video_note_to_dict(message: Message) -> tuple[dict, dict | None]:
        data = {
            'data': message.video_note.file_id,
        }

        return data, util.extract_buttons(message)

    @staticmethod
    def contact_to_dict(message: Message) -> tuple[dict, dict | None]:
        data = {
            'phone_number': message.contact.phone_number,
            'first_name': message.contact.first_name,
            'last_name': message.contact.last_name,
        }

        return data, util.extract_buttons(message)

    @staticmethod
    def text_to_dict(message: Message) -> tuple[dict, dict | None]:
        data = {
            'text': message.text,
            'parse_mode': 'HTML'
        }

        return data, util.extract_buttons(message)

    @staticmethod
    def sticker_to_dict(message: Message) -> tuple[dict, dict | None]:
        data = {
            'sticker': message.sticker.file_id
        }

        return data, util.extract_buttons(message)

    @staticmethod
    def dice_to_dict(message: Message) -> tuple[dict, dict | None]:
        data = {
            'emoji': message.dice.emoji
        }

        return data, util.extract_buttons(message)

    @staticmethod
    def voice_to_dict(message: Message) -> tuple[dict, dict | None]:
        data = {
            'voice': message.voice.file_id
        }

        return data, util.extract_buttons(message)

    @staticmethod
    def document_to_dict(message: Message) -> tuple[dict, dict | None]:
        data = {
            'document': message.document.file_id,
            'caption': message.caption,
            'parse_mode': 'HTML'
        }

        return data, util.extract_buttons(message)

    def __call__(self, message: Message) -> None:
        to_send, buttons = self.TYPES[message.content_type](message)
        self.jsons = json.dumps(to_send, ensure_ascii=False), json.dumps(buttons, ensure_ascii=False)
        self.is_called = True

    def __str__(self) -> str:
        if not self.is_called:
            raise NotImplementedError('Перед преобразованием в строку необходимо вызвать объект класса!')

        return "<b>json текста, медиа и параметров форматирования:</b>\n<code>{}</code>\n\n<b>json " \
               "кнопок:</b>\n<code>{}</code>".format(*self.jsons)
