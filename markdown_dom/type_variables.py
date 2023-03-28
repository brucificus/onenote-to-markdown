from typing import TypeVar, Callable, Optional

import panflute

T = TypeVar('T')

PanfluteElementFilter = Callable[[panflute.Element, panflute.Doc, ...], Optional[panflute.Element]]
PanfluteDocumentFilter = Callable[[panflute.Doc], None]
PanfluteElementPredicate = Callable[[panflute.Element, ...], bool]
PanfluteImageElementUrlProjection = Callable[[panflute.Image, panflute.Doc], str]
PanfluteElementAccumulatorFunc = Callable[[panflute.Element, panflute.Doc, T], T]
