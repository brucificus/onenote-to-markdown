import enum
from enum import Enum


@enum.unique
class YearMonthDayDigitsComponentOrder(str, Enum):
    YMD = 'ymd'
    DMY = 'dmy'
    MDY = 'mdy'

    def __str__(self):
        return self.value
