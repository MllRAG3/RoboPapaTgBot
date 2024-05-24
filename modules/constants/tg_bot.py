from modules.constants.config import BOT_TKN

from typing import Final
from telebot import TeleBot


BOT: Final[TeleBot] = TeleBot(BOT_TKN)
