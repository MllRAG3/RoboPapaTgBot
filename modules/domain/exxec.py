import random
import time
import datetime
try:
    import ujson as json
except ImportError:
    import json

from telebot.types import Message, User, InlineKeyboardMarkup, InlineKeyboardButton
from modules.constants.tg_bot import BOT
from modules.database.models.requireds import Requires
from modules.domain.json_reader import JsonReader
from modules.database.models.users import TgUser

CONTEXT: dict = {'context': '', 'dice': -1}


class Exec:
    def __init__(self, message: Message, user: User | None = None):
        """
        :param message: Объект класса telebot.types.Message - информация обо всем контексте общения с ботом
        """
        self.message: Message = message
        self.tb_user: User = message.from_user if user is None else user
        self.chat_id = message.chat.id
        self.database_user: TgUser = TgUser.get_or_create(telegram_id=self.tb_user.id)[0]

        print(self.database_user.last_activity)
        self.database_user.last_activity = datetime.datetime.now()
        print(self.database_user.last_activity)
        TgUser.save(self.database_user)

    def send(self, type_value, type='text', **kwargs):
        """
        Отправляет новое сообщение
        :param type_value: основное значение для выбранного метода отправки (для текст. сообщения - text)
        подробнее см. modules/types/util
        :param type: Тип сообщения (text - текстовое сообщение, подробнее см. modules/types/util)
        :param kwargs: дополнительные параметры при отправке
        (ключи должны совпадать с именованными аргументами TeleBot.send_message(...))
        :return:
        """
        match type:
            case 'text':
                BOT.send_chat_action(self.chat_id, 'typing')
                time.sleep(random.randint(1, 5))
                BOT.send_message(chat_id=self.chat_id, text=type_value, **kwargs)
            case 'photo':
                BOT.send_chat_action(self.chat_id, 'upload_photo')
                time.sleep(random.randint(1, 5))
                BOT.send_photo(self.chat_id, photo=open(type_value, 'rb'), **kwargs)  # has caption
            case 'sticker':
                BOT.send_chat_action(self.chat_id, 'choose_sticker')
                time.sleep(random.randint(1, 5))
                BOT.send_sticker(self.chat_id, sticker=type_value, **kwargs)
            case 'dice':
                BOT.send_chat_action(self.chat_id, 'choose_sticker')
                time.sleep(random.randint(1, 5))
                return BOT.send_dice(self.chat_id, emoji=type_value, **kwargs).dice.value  # allowed type_value: 🎲🎯🏀⚽🎳🎰
            case 'voice':
                BOT.send_chat_action(self.chat_id, 'record_voice')
                time.sleep(random.randint(1, 5))
                BOT.send_chat_action(self.chat_id, 'upload_voice')
                time.sleep(random.randint(1, 5))
                BOT.send_voice(self.chat_id, voice=open(type_value, 'rb'), **kwargs)  # has caption
            case 'contact':
                BOT.send_chat_action(self.chat_id, 'typing')
                time.sleep(random.randint(1, 5))
                BOT.send_contact(self.chat_id, phone_number=type_value, **kwargs)  # ВАЖНО! в kwargs должен
                # присутствовать аргумент first_name!
            case 'document':
                BOT.send_chat_action(self.chat_id, 'upload_document')
                time.sleep(random.randint(1, 5))
                BOT.send_document(self.chat_id, open(type_value, 'rb'), **kwargs)  # has caption
            case 'animation':
                BOT.send_chat_action(self.chat_id, 'record_video')
                time.sleep(random.randint(1, 5))
                BOT.send_chat_action(self.chat_id, 'upload_video')
                time.sleep(random.randint(1, 5))
                BOT.send_animation(self.chat_id, animation=open(type_value, 'rb'), **kwargs)  # has caption
            case 'video_note':
                BOT.send_chat_action(self.chat_id, 'record_video_note')
                time.sleep(random.randint(1, 5))
                BOT.send_chat_action(self.chat_id, 'upload_video_note')
                time.sleep(random.randint(1, 5))
                BOT.send_video_note(self.chat_id, data=open(type_value, 'rb'), **kwargs)
            case _:
                raise TypeError('Указан неверный тип формата сообщения! Допустимые значения см. modules/types/util')

        return 0

    def start(self):
        """
        Обрабатывает команду /start
        :return:
        """
        if not self.check_all_subs():
            self.send('Вы не подписались на все необходимые каналы!')
            self.send(
                'Список каналов, на которые нужно подписаться:\n',
                reply_markup=InlineKeyboardMarkup(row_width=1).add(*map(lambda x: InlineKeyboardButton(f'Канал {x.id}', url=f'https://t.me/{x.channel_link}'.replace('@', '')), Requires.select()))
            )
            return
        self.send('Привет! О чем поболтаем?')

    def check_all_subs(self):
        """
        Проверяет, подписан ли пользователь на все каналы в таблице Requires
        :return:
        """
        for channel in Requires.select():
            try:
                BOT.get_chat_member(chat_id=channel.channel_link, user_id=self.tb_user.id)
            except Exception as e:
                error = e
                return False  # user not found in current channel
        return True

    def send_answer(self, message: Message):
        """
        Отправляет ответ из таблицы Replica с наибольшим совпадением текста сообщения и
        колонки key
        :param message: сообщение (передается автоматически методом TeleBot.register_next_step_handler(...))
        :return:
        """
        global CONTEXT
        for to_send in JsonReader(message, CONTEXT)():
            CONTEXT['context'] = to_send['type_value']
            CONTEXT['dice'] = self.send(**to_send)
