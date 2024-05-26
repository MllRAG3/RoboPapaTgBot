import random
import time
import json

from telebot.types import Message, User, InlineKeyboardMarkup, InlineKeyboardButton
from modules.constants.tg_bot import BOT
from modules.constants.morph import R_ANAL
from modules.database.models.requireds import Requires
from modules.database.models.replicas import Key, Answer

CONTEXT: dict = {'context': '', 'dice': -1}


class Exec:
    def __init__(self, message: Message, user: User | None = None):
        """
        :param message: Объект класса telebot.types.Message - информация обо всем контексте общения с ботом
        """
        self.message: Message = message
        self.tb_user: User = message.from_user if user is None else user
        self.chat_id = message.chat.id

    def send(self, type_value, type='text', **additional):
        """
        Отправляет новое сообщение
        :param type_value: основное значение для выбранного метода отправки (для текст. сообщения - text)
        подробнее см. modules/types/util
        :param type: Тип сообщения (text - текстовое сообщение, подробнее см. modules/types/util)
        :param additional: дополнительные параметры при отправке
        (ключи должны совпадать с именованными аргументами TeleBot.send_message(...))
        :return:
        """
        match type:
            case 'text':
                BOT.send_chat_action(self.chat_id, 'typing')
                time.sleep(random.randint(1, 5))
                BOT.send_message(chat_id=self.chat_id, text=type_value, **additional)
            case 'photo':
                BOT.send_chat_action(self.chat_id, 'upload_photo')
                time.sleep(random.randint(1, 5))
                BOT.send_photo(self.chat_id, photo=open(type_value, 'rb'), **additional)  # has caption
            case 'sticker':
                BOT.send_chat_action(self.chat_id, 'choose_sticker')
                time.sleep(random.randint(1, 5))
                BOT.send_sticker(self.chat_id, sticker=type_value, **additional)
            case 'dice':
                BOT.send_chat_action(self.chat_id, 'choose_sticker')
                time.sleep(random.randint(1, 5))
                return BOT.send_dice(self.chat_id, emoji=type_value, **additional).dice.value  # allowed type_value: 🎲🎯🏀⚽🎳🎰
            case 'voice':
                BOT.send_chat_action(self.chat_id, 'record_voice')
                time.sleep(random.randint(1, 5))
                BOT.send_chat_action(self.chat_id, 'upload_voice')
                time.sleep(random.randint(1, 5))
                BOT.send_voice(self.chat_id, voice=open(type_value, 'rb'), **additional)  # has caption
            case 'contact':
                BOT.send_chat_action(self.chat_id, 'typing')
                time.sleep(random.randint(1, 5))
                BOT.send_contact(self.chat_id, phone_number=type_value, **additional)  # ВАЖНО! в additional должен
                # присутствовать аргумент first_name!
            case 'document':
                BOT.send_chat_action(self.chat_id, 'upload_document')
                time.sleep(random.randint(1, 5))
                BOT.send_document(self.chat_id, open(type_value, 'rb'), **additional)  # has caption
            case 'animation':
                BOT.send_chat_action(self.chat_id, 'record_video')
                time.sleep(random.randint(1, 5))
                BOT.send_chat_action(self.chat_id, 'upload_video')
                time.sleep(random.randint(1, 5))
                BOT.send_animation(self.chat_id, animation=open(type_value, 'rb'), **additional)  # has caption
            case 'video_note':
                BOT.send_chat_action(self.chat_id, 'record_video_note')
                time.sleep(random.randint(1, 5))
                BOT.send_chat_action(self.chat_id, 'upload_video_note')
                time.sleep(random.randint(1, 5))
                BOT.send_video_note(self.chat_id, data=open(type_value, 'rb'), **additional)
            case _:
                raise TypeError('Указан неверный тип формата сообщения! Допустимые значения см. modules/types/util')

        return -1

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
                BOT.get_chat_member(chat_id=channel.channel_link, user_id=self.tb_user.id)
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
        global CONTEXT
        print(CONTEXT)
        percent_results = []

        for key in Key.select():
            dict_k = json.loads(key.key)
            if set(dict_k.keys()) != {'dice', 'by_user', 'by_bot'}:
                raise KeyError('В словаре (таблица Key) недостаточно ключей! Необходимы: {"dice", "by_user", "by_bot"}')

            exp_user_ans = list(map(lambda x: R_ANAL.parse(x)[0].word.lower(), dict_k['by_user'].split()))
            exp_context = list(map(lambda x: R_ANAL.parse(x)[0].word.lower(), dict_k['by_bot'].split()))
            exp_dice = dict_k['dice']
            if CONTEXT != {}:
                same = 0
                same += sum([int(R_ANAL.parse(w)[0].word.lower() in exp_user_ans) for w in message.text.split()])
                print(same)
                same += sum([int(R_ANAL.parse(w)[0].word.lower() in exp_context) for w in CONTEXT['context'].split()])
                print(same)
                if CONTEXT['dice'] != -1:
                    same += int(abs(CONTEXT['dice'] - exp_dice))
                print(same)
            else:
                same = 0
                same += sum([int(R_ANAL.parse(w)[0].word.lower() in exp_user_ans) for w in message.text.split()])

            percent_results.append((key, (same / len(message.text.split())) * 100))

        ans: Answer = random.choice(max(percent_results, key=lambda x: x[1])[0].answers)
        ans_to_send = json.loads(ans.texts_json)[0]
        if set(ans_to_send) != {'type', 'additional', 'par'}:
            raise KeyError('Недостаточно ключей! (Необходимы: {"type", "additional", "par"})')
        CONTEXT = {'context': ans_to_send['par'], 'dice': int(self.send(type_value=ans_to_send['par'], type=ans_to_send['type'], **json.loads(ans_to_send['additional'])))}
        if len(json.loads(ans.texts_json)) > 1:
            self.send_next(ans.id)
        self.reg_user_input()

    def send_next(self, ans_id, ind=1):
        global CONTEXT
        ans: Answer = Answer.get_by_id(ans_id)
        print(json.loads(ans.texts_json))
        ans_to_send = json.loads(ans.texts_json)[ind]
        if len(json.loads(ans.texts_json)) - 1 > ind:
            self.send_next(ans.id, ind=(ind + 1))
        CONTEXT = {'context': ans_to_send['par'], 'dice': int(self.send(type_value=ans_to_send['par'], type=ans_to_send['type'], **json.loads(ans_to_send['additional'])))}
