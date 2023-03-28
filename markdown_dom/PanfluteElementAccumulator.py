import panflute
from typing import Generic, ContextManager, Tuple, Optional

from markdown_dom.type_variables import PanfluteElementFilter, PanfluteElementPredicate, PanfluteElementAccumulatorFunc, T


class PanfluteElementAccumulator(Generic[T], ContextManager[Tuple[PanfluteElementFilter, Optional[PanfluteElementPredicate]]]):
    def __init__(self, accumulator: PanfluteElementAccumulatorFunc, seed: Optional[T] = None, stop_if: Optional[PanfluteElementPredicate] = None):
        self._accumulator = accumulator
        self._result: T = seed
        self._stop_if = stop_if
        self._is_complete = False

    def __enter__(self) -> (PanfluteElementFilter, Optional[PanfluteElementPredicate]):
        return self._element_filter, self._stop_if

    def _element_filter(self, element: panflute.Element, doc: panflute.Doc):
        if self._is_complete:
            raise ValueError("Cannot accumulate more elements after walk is complete")
        self._result = self._accumulator(element, doc, self._result)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._is_complete = True

    @property
    def result(self) -> T:
        if not self._is_complete:
            raise ValueError("Cannot retrieve accumulated value before walk is complete")

        return self._result
