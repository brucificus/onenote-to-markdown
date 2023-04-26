from collections.abc import Sequence
from typing import TypeVar, Callable, Optional, Iterable, Union, Type, Tuple

import panflute


T = TypeVar('T')


PanfluteElementContainerElementCtor = Union[Type[panflute.Element], Callable[[*Tuple[panflute.Element, ...]], panflute.Element]]
PanfluteElementCtor = Union[Type[panflute.Element], Callable[[], panflute.Element]]

PanfluteElementLikeSingular = Union[panflute.Element, str, PanfluteElementCtor, PanfluteElementContainerElementCtor]
PanfluteElementLike = Union[
    PanfluteElementLikeSingular,
    Sequence[PanfluteElementLikeSingular],
    Iterable[PanfluteElementLikeSingular]
]


PanfluteElementFilter = Callable[[panflute.Element, panflute.Doc], Optional[PanfluteElementLike]]
PanfluteDocumentFilter = Callable[[panflute.Doc], None]
PanfluteElementPredicate = Callable[[panflute.Element], bool]
PanfluteImageElementUrlProjection = Callable[[panflute.Image, panflute.Doc], str]
PanfluteElementAccumulatorFunc = Callable[[panflute.Element, panflute.Doc, T], T]


PanfluteElementStyleValuePredicateSingular = Union[str, Callable[[str], bool], Callable[[float, str], bool]]
PanfluteElementStyleValuePredicate = Union[PanfluteElementStyleValuePredicateSingular, Sequence[PanfluteElementStyleValuePredicateSingular], Iterable[PanfluteElementStyleValuePredicateSingular]]


def normalize_elementlike(elementlike: PanfluteElementLike, *, sequence_type: Optional[Union[Type[Sequence], Callable[[Iterable], Sequence]]] = tuple) -> Sequence[panflute.Element]:
    if elementlike is None:
        raise ValueError('elementlike cannot be None')

    if isinstance(elementlike, str):
        return normalize_elementlike(panflute.Str(elementlike), sequence_type=sequence_type)

    if callable(elementlike):
        return normalize_elementlike(elementlike(), sequence_type=sequence_type)

    if sequence_type:
        if isinstance(elementlike, panflute.Element):
            return sequence_type((elementlike,))
        if isinstance(elementlike, (Sequence, Iterable)):
            return sequence_type(e2 for e2 in (normalize_elementlike(e, sequence_type=None) for e in elementlike))
        raise ValueError(f'Unexpected elementlike type: {type(elementlike)}')

    if isinstance(elementlike, panflute.Element):
        return elementlike
    if isinstance(elementlike, Sequence) and len(elementlike) == 1:
        return normalize_elementlike(elementlike[0], sequence_type=None)
    if isinstance(elementlike, (Sequence, Iterable)):
        return sequence_type(e2 for e2 in (normalize_elementlike(e, sequence_type=None) for e in elementlike))
    raise ValueError(f'Unexpected elementlike type: {type(elementlike)}')
