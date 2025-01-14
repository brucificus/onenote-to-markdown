from typing import TypeVar, Callable, Optional, Sequence, Iterable, Union

import panflute

T = TypeVar('T')

PanfluteElementFilter = Callable[[panflute.Element, panflute.Doc, ...], Optional[panflute.Element]]
PanfluteDocumentFilter = Callable[[panflute.Doc], None]
PanfluteElementPredicate = Callable[[panflute.Element, ...], bool]
PanfluteImageElementUrlProjection = Callable[[panflute.Image, panflute.Doc], str]
PanfluteElementAccumulatorFunc = Callable[[panflute.Element, panflute.Doc, T], T]


PanfluteElementLikeSingular = Union[panflute.Element, str]
PanfluteElementLike = Union[
    PanfluteElementLikeSingular,
    Sequence[PanfluteElementLikeSingular],
    Iterable[PanfluteElementLikeSingular]
]


def normalize_elementlike(elementlike: PanfluteElementLike) -> Sequence[panflute.Element]:
    if isinstance(elementlike, str):
        return (panflute.Str(elementlike),)
    elif isinstance(elementlike, panflute.Element):
        return (elementlike,)
    elif isinstance(elementlike, Sequence):
        return tuple(normalize_elementlike(e) for e in elementlike)
    elif isinstance(elementlike, Iterable):
        return tuple(normalize_elementlike(e) for e in elementlike)
    elif elementlike is None:
        return tuple()
    else:
        return elementlike
