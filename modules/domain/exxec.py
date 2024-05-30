import random
import time
import schedule
from datetime import datetime, timedelta

try:
    import ujson as json
except ImportError:
    import json

from telebot.types import Message, User, InlineKeyboardMarkup, InlineKeyboardButton, ChatMember, ChatMemberMember
import telebot.util as tb_util
from telebot.apihelper import ApiTelegramException

from modules.constants.tg_bot import BOT
import modules.constants.message_texts as m_texts
import modules.domain.util as util
from modules.database.models.requireds import Requires
from modules.domain.json_reader import JsonReader
from modules.database.models.users import TgUser
from modules.database.models.mailing_messages import MailingMessages

CONTEXT: dict = {'context': '', 'dice': -1}


class DynamicPicCounter:
    def __init__(self, message: Message):
        """
        Аттрибуты:

        message (telebot.types.Message):
          вся информация о сеансе с пользователем
        is_working (bool):
          Статус работы алгоритма (True если работает)
        most_active_hour (int):
          Час, за который к боту обращались больше всего раз
        """
        self.message: Message = message
        self.is_working: bool = True
        self.most_active_hour: int = 0
        schedule.every().day.at("00:00").do(self.count_activity).tag("auto-update-user-activity")

    def stop_algorythm(self) -> None:
        """
        Останавливает алгоритм
        :return:
        """
        self.is_working = False

    def count_activity(self, restart=True) -> None:
        """
        Высчитывает час, за который к боту обращались больше всего раз и
        присваивает это значение аттрибуту self.most_active_hour
        :param restart: Перезапустить основной алгоритм рассылки
        :return:
        """
        activity = []
        for i in range(24):
            activity.append({"hour": i, "users": len(TgUser.select().where((TgUser.last_activity.hour == i)))})
        self.most_active_hour = max(activity, key=lambda y: y["users"])["hour"]
        if not restart:
            return
        self.stop_algorythm()
        schedule.clear("send-mailing")
        self.start_algorythm()

    def send_all(self) -> None:
        """
        Отправляет все рекламные рассылки каждому из зарегистрированных пользователей
        :return:
        """
        for ads in MailingMessages.select().where(MailingMessages.is_active):
            for chat_id in map(lambda x: x.chat_id, TgUser.select()):
                try:
                    Exec(self.message).send(
                        chat_id=chat_id,
                        type=ads.type,
                        content_json=ads.send_data_json,
                        buttons_json=ads.send_data_buttons_json
                    )
                    ads.send_at = datetime.now() + timedelta(days=1)
                    MailingMessages.save(ads)
                except ApiTelegramException:
                    pass
                time.sleep(1)

    def start_algorythm(self) -> None:
        """
        Запускает алгоритм рассылок
        :return:
        """
        self.is_working = True
        self.count_activity(restart=False)
        schedule.every()\
            .day\
            .at(f"{str(self.most_active_hour - 1).rjust(2, '0')}:00")\
            .do(self.send_all).tag("send-mailing")

        while self.is_working:
            schedule.run_pending()
            time.sleep(600)


class Exec:
    def __init__(self, message: Message, user: User | None = None):
        """
        :param message: Объект класса telebot.types.Message - информация обо всем контексте общения с ботом
        """
        self.message: Message = message
        self.tb_user: User = message.from_user if user is None else user
        self.chat_id = message.chat.id
        self.database_user: TgUser = TgUser.get_or_create(telegram_id=self.tb_user.id, chat_id=self.chat_id)[0]

        self.database_user.last_activity = datetime.now()
        TgUser.save(self.database_user)

    def edit(self, **data):
        try:
            BOT.edit_message_text(**data, message_id=self.message.id, chat_id=self.chat_id)
        except ApiTelegramException:
            self.send(
                'text',
                content_json=util.convert_text_message_to_json(m_texts.MESSAGE_TO_EDIT_NOT_FOUND_ERROR),
                buttons_json='{}'
            )
            BOT.edit_message_text(**data, message_id=self.message.id+1, chat_id=self.chat_id)

    def send(self, type: str, content_json: str, buttons_json: str | None, chat_id=None):
        content = json.loads(content_json)
        markup = InlineKeyboardMarkup.de_json(buttons_json if buttons_json != '{}' else None)
        if chat_id is None:
            chat_id = self.chat_id

        match type:
            case 'text':
                BOT.send_chat_action(chat_id, 'typing')
                time.sleep(random.randint(1, 5))
                BOT.send_message(chat_id=chat_id, **content, reply_markup=markup)
            case 'photo':
                BOT.send_chat_action(chat_id, 'upload_photo')
                time.sleep(random.randint(1, 5))
                BOT.send_photo(chat_id, **content, reply_markup=markup)  # has caption
            case 'sticker':
                BOT.send_chat_action(chat_id, 'choose_sticker')
                time.sleep(random.randint(1, 5))
                BOT.send_sticker(chat_id, **content, reply_markup=markup)
            case 'dice':
                BOT.send_chat_action(chat_id, 'choose_sticker')
                time.sleep(random.randint(1, 5))
                return BOT.send_dice(chat_id, **content, reply_markup=markup).dice.value  # allowed type_value: 🎲🎯🏀⚽🎳🎰
            case 'voice':
                BOT.send_chat_action(chat_id, 'record_voice')
                time.sleep(random.randint(1, 5))
                BOT.send_chat_action(chat_id, 'upload_voice')
                time.sleep(random.randint(1, 5))
                BOT.send_voice(chat_id, **content, reply_markup=markup)  # has caption
            case 'contact':
                BOT.send_chat_action(chat_id, 'typing')
                time.sleep(random.randint(1, 5))
                BOT.send_contact(chat_id, **content, reply_markup=markup)  # ВАЖНО! в kwargs должен
                # присутствовать аргумент first_name!
            case 'document':
                BOT.send_chat_action(chat_id, 'upload_document')
                time.sleep(random.randint(1, 5))
                BOT.send_document(chat_id, **content, reply_markup=markup)  # has caption
            case 'video':
                BOT.send_chat_action(chat_id, 'record_video')
                time.sleep(random.randint(1, 5))
                BOT.send_chat_action(chat_id, 'upload_video')
                time.sleep(random.randint(1, 5))
                BOT.send_video(chat_id, **content, reply_markup=markup)  # has caption
            case 'video_note':
                BOT.send_chat_action(chat_id, 'record_video_note')
                time.sleep(random.randint(1, 5))
                BOT.send_chat_action(chat_id, 'upload_video_note')
                time.sleep(random.randint(1, 5))
                BOT.send_video_note(chat_id, **content, reply_markup=markup)
            case _:
                raise NotImplementedError(f'Тип сообщений >>{type}<< не может быть отправлен данным методом!')

        return 0

    def start(self):
        """
        Обрабатывает команду /start
        :return:
        """
        if self.check_all_subs():
            buttons = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton('Начать общаться с папочкой', callback_data="start_talking"),
                InlineKeyboardButton('Настройки', callback_data="settings")
            )
            self.edit(text=m_texts.SUBSCRIBED_MESSAGE, reply_markup=buttons)
            return

        buttons = InlineKeyboardMarkup(row_width=1)\
            .add(*map(lambda x: InlineKeyboardButton(f'Канал {x.id}', url=x.channel_link), Requires.select()))\
            .add(InlineKeyboardButton("✅ПРОВЕРИТЬ ПОДПИСКИ✅", callback_data='check_subs'))

        self.edit(text=m_texts.NOT_SUBSCRIBED_MESSAGE, reply_markup=buttons)

    def start_talking(self):
        self.edit(text=m_texts.START_TALKING_MESSAGE)

    def settings(self):
        buttons = InlineKeyboardMarkup().row(
            InlineKeyboardButton('Предложка', url='https://t.me/RobopapochkaSupport_Bot'),
            InlineKeyboardButton('Главная', callback_data='check_subs')
        )
        self.edit(text=m_texts.SETTINGS_MESSAGE, reply_markup=buttons)

    def check_all_subs(self):
        """
        Проверяет, подписан ли пользователь на все каналы в таблице Requires
        :return:
        """
        for channel in Requires.select():
            user: ChatMember = BOT.get_chat_member(chat_id=channel.channel_id, user_id=self.tb_user.id)
            if not isinstance(user, ChatMemberMember):
                return False

        return True

    def send_answer(self, message: Message):
        """
        Отправляет ответ из таблицы Replica с наибольшим совпадением текста сообщения и
        колонки key
        :param message: сообщение (передается автоматически методом TeleBot.register_next_step_handler(...))
        :return:
        """
        global CONTEXT
        if tb_util.is_command(message.text):
            return

        context_in = {
            'photo': "caption",
            'video': "caption",
            'video_note': "data",
            'contact': "first_name",
            'text': "text",
            'sticker': "sticker",
            'dice': "emoji",
            'voice': "caption",
            'document': "caption",
        }
        for to_send in JsonReader(message, CONTEXT)():
            CONTEXT['context'] = json.loads(to_send['content_json'])[context_in[to_send['type']]]
            CONTEXT['dice'] = self.send(**to_send)
