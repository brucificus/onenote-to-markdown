import enum
from enum import Enum


@enum.unique
class AbbrevYearPrefix(str, Enum):
    Nineteen = '19'
    Twenty = '20'
