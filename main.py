from telebot.types import Message
from modules.constants.tg_bot import BOT
from modules.domain.exxec import Exec
from modules.database.util.create_all import create_all_database_tables


@BOT.message_handler(commands=['start'])
def start(message: Message):
    Exec(message).start()


if __name__ == '__main__':
    create_all_database_tables()
    BOT.infinity_polling()
    print('Bot has been started successfully!')
