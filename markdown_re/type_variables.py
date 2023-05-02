import re

from collections.abc import Sequence
from typing import TypeVar, Union, Iterable

import panflute


T = TypeVar('T')


PatternLike = Union[str, re.Pattern[str]]


PanfluteElementLikeSingular = Union[panflute.Element, str]
PanfluteElementLike = Union[
    PanfluteElementLikeSingular,
    Sequence[PanfluteElementLikeSingular],
    Iterable[PanfluteElementLikeSingular]
]


def normalize_elementlike(elementlike: PanfluteElementLike) -> Sequence[panflute.Element]:
    if isinstance(elementlike, str):
        return (panflute.Str(elementlike),)
    if isinstance(elementlike, panflute.Element):
        return (elementlike,)
    if isinstance(elementlike, Sequence):
        return tuple(normalize_elementlike(e) for e in elementlike)
    if isinstance(elementlike, Iterable):
        return tuple(normalize_elementlike(e) for e in elementlike)
    if elementlike is None:
        return tuple()
    return elementlike
