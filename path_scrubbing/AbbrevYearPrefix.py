import enum
from enum import Enum


@enum.unique
class AbbrevYearPrefix(str, Enum):
    NINETEEN = '19'
    TWENTY = '20'
