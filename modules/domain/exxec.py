from telebot.types import Message, User, InlineKeyboardMarkup, InlineKeyboardButton
from modules.constants.tg_bot import BOT
from modules.database.models.users import Users, Subscribed
from modules.database.models.requireds import Requires
from modules.database.models.replicas import Replica


class Exec:
    def __init__(self, message: Message, user: User | None = None):
        self.message: Message = message
        self.telebot_user: User = message.from_user if user is None else user

        self.db_user: Users | None = None
        self.load_or_create_db_user()

    def load_or_create_db_user(self):
        try:
            self.db_user = Users.get(tg_id=self.telebot_user.id)
        except AttributeError:
            data = {'tg_id': self.telebot_user.id, 'username': self.telebot_user.username}
            new_user = Users.create(**data)
            self.db_user = new_user

    def send(self, text, **additional):
        BOT.send_message(chat_id=self.message.chat.id, text=text, **additional)

    def start(self):
        if not self.check_all_subs():
            self.send('Вы не подписались на все необходимые каналы!')
            self.send(
                'Список каналов, на которые нужно подписаться:\n',
                reply_markup=InlineKeyboardMarkup(row_width=1).add(*map(lambda x: InlineKeyboardButton(f'Канал {x.id}', url=f'https://t.me/{x.channel_id}'), Requires.select()))
            )
            return
        self.send('Привет! О чем поболтаем?')
        self.reg_user_input()

    def check_all_subs(self):
        recs = Requires.select()
        for r in recs:
            try:
                BOT.get_chat_member(chat_id=r.channel_id, user_id=self.telebot_user.id)
                if Subscribed.select().where(Subscribed.chan_id == r.channel_id):
                    continue
                Subscribed.create(user=self.db_user, chan_id=r.channel_id)
            except Exception as e:
                not_found = e
                return False

        return True

    def reg_user_input(self):
        BOT.register_next_step_handler(self.message, callback=self.send_answer)

    def send_answer(self, message: Message):
        reps = Replica.select().where(Replica.key.contains(message.text))
        if not reps:
            self.send('Ты сказал какую-то чепуху, я тебя не понимаю, черт возьми! Можешь повторить?')
        self.send(reps[0].answer)
