"""Анализатор русских слов (Для алгоритмов сравнения)"""
from pymorphy3 import MorphAnalyzer
from typing import Final


R_ANAL: Final[MorphAnalyzer] = MorphAnalyzer(lang='ru')
