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
            'video_note': ...,
            'contact': ...,
            'text': ...,
            'sticker': ...,
            'dice': ...,
            'voice': ...,
            'document': ...,
        }
        self.jsons: tuple[str, str] = ('null', 'null')
        self.is_called: bool = False

    @staticmethod
    def photo_message_to_dict(message: Message) -> tuple[dict, dict | None]:
        to_send = {
            'photo': message.photo[0].file_id,
            'caption': message.caption,
            'parse_mode': 'HTML',
            'protect_content': int(bool(message.has_protected_content))}
        buttons = message.reply_markup
        if buttons:
            buttons = buttons.to_dict()
        return to_send, buttons

    @staticmethod
    def video_message_to_dict(message: Message) -> tuple[dict, dict | None]:
        to_send = {
            'video': message.video.file_id,
            'caption': message.caption,
            'parse_mode': 'HTML',
            'protect_content': int(bool(message.has_protected_content))}
        buttons = message.reply_markup
        if buttons:
            buttons = buttons.to_dict()
        return to_send, buttons

    def __call__(self, message: Message) -> None:
        to_send, buttons = self.TYPES[message.content_type](message)
        self.jsons = json.dumps(to_send, ensure_ascii=False), json.dumps(buttons, ensure_ascii=False)
        self.is_called = True

    def __str__(self):
        return "<b>json текста, медиа и параметров форматирования:</b>\n<code>{}</code>\n\n" \
               "<b>json кнопок:</b>\n<code>{}</code>".format(*self.jsons)
