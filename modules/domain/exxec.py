from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from modules.constants.tg_bot import BOT
from modules.constants.morph import R_ANAL
from modules.database.models.requireds import Requires
from modules.database.models.replicas import Replica


class Exec:
    def __init__(self, message: Message):
        """
        :param message: Объект класса telebot.types.Message - информация обо всем контексте общения с ботом
        """
        self.message: Message = message

    def send(self, text, **additional):
        """
        Отправляет новое сообщение
        :param text: текст сообщения
        :param additional: дополнительные параметры при отправке
        (ключи должны совпадать с именованными аргументами TeleBot.send_message(...))
        :return:
        """
        BOT.send_message(chat_id=self.message.chat.id, text=text, **additional)

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
        self.reg_user_input()

    def check_all_subs(self):
        """
        Проверяет, подписан ли пользователь на все каналы в таблице Requires
        :return:
        """
        for channel in Requires.select():
            try:
                BOT.get_chat_member(chat_id=channel.channel_link, user_id=self.message.from_user.id)
            except Exception as e:
                error = e
                return False  # user not found in current channel
        return True

    def reg_user_input(self):
        """
        Обрабатывает следующее отправленное сообщение
        :return:
        """
        BOT.register_next_step_handler(self.message, callback=self.send_answer)

    def send_answer(self, message: Message):
        """
        Отправляет ответ из таблицы Replica с наибольшим совпадением текста сообщения и
        колонки key
        :param message: сообщение (передается автоматически методом TeleBot.register_next_step_handler(...))
        :return:
        """
        best = []

        for rep in Replica.select():
            same = 0
            base = list(map(lambda x: R_ANAL.parse(x)[0].word.lower(), rep.key.split()))
            for w in message.text.split():
                same += int(R_ANAL.parse(w)[0].word.lower() in base)
            same_percent = (same / len(message.text.split())) * 100
            best.append((rep, same_percent))

        best = max(best, key=lambda x: x[1])
        if best[1] < 5.0:
            self.send('Я тебя не понимаю! Ты сказал что-то невнятное, повтори')
            self.reg_user_input()
            return
        self.send(best[0].answer)
        self.reg_user_input()
