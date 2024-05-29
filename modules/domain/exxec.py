import random
import time
from schedule import every, run_pending
from datetime import datetime, timedelta

try:
    import ujson as json
except ImportError:
    import json

from telebot.types import Message, User, InlineKeyboardMarkup, InlineKeyboardButton, ChatMember, ChatMemberMember
from modules.constants.tg_bot import BOT
from modules.database.models.requireds import Requires
from modules.domain.json_reader import JsonReader
from modules.database.models.users import TgUser
from modules.database.models.mailing_messages import MailingMessages

CONTEXT: dict = {'context': '', 'dice': -1}


class DynamicPicCounter:
    def __init__(self, message: Message):
        self.message: Message = message
        self.is_working: bool = True
        self.most_active_hour: int = 19

    def count_activity(self, n=1):
        activity = []
        day_now = datetime.now().day
        for i in range(24):
            activity.append({"hour": i, "users": TgUser.select().where(
                (TgUser.last_activity.day == (day_now - 1)) &
                (TgUser.last_activity.hour == i)
            )})
        self.most_active_hour = list(map(lambda x: x["hour"], sorted(activity, key=lambda y: y["users"])[:n]))

    def send_all(self):
        for chat_id in map(lambda x: x.chat_id, TgUser.select()):
            for ads in MailingMessages\
                    .select()\
                    .where(
                        (MailingMessages.send_quantity > 0) &
                        (MailingMessages.send_at < datetime.now()) &
                        MailingMessages.is_active
                    ):
                try:
                    Exec(self.message).send(
                        chat_id=chat_id,
                        type=ads.type,
                        content_json=ads.send_data_json,
                        buttons_json=ads.send_data_buttons_json
                    )
                    ads.send_at = datetime.now() + timedelta(days=1)
                    MailingMessages.save(ads)
                except Exception as e:
                    err = e
                    print(err)  # for debug
            time.sleep(0.5)

    def __call__(self):
        every().day.at("00:00").do(self.count_activity)
        every().day.at(f"{self.most_active_hour}:00").do(self.send_all)
        while self.is_working:
            run_pending()
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

    def start_mailing(self):
        dc = DynamicPicCounter(self.message)
        dc()

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
        if not self.check_all_subs():
            self.send("text", '{"text": "Вы не подписались на все необходимые каналы!"}', '{}')
            text = '{"text": "Список каналов, на которые нужно подписаться:"}'
            buttons = InlineKeyboardMarkup(row_width=1).add(
                *map(lambda x: InlineKeyboardButton(f'Канал {x.id}', url=f'https://t.me/{x.channel_link}'), Requires.select())
            )
            buttons.add(InlineKeyboardButton("✅ПРОВЕРИТЬ ПОДПИСКИ✅", callback_data='check_subs'))
            self.send('text', text, json.dumps(buttons.to_dict(), ensure_ascii=False))
            return
        self.send('text', '{"text": "Привет! О чем поболтаем?"}', '{}')

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
        for to_send in JsonReader(message, CONTEXT)():
            CONTEXT['context'] = to_send['type_value']
            CONTEXT['dice'] = self.send(**to_send)
