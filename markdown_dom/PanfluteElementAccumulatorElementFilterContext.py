import panflute
from typing import Generic, ContextManager, Tuple, Optional, Any

from markdown_dom.type_variables import PanfluteElementFilter, PanfluteElementPredicate, PanfluteElementAccumulatorFunc, T


class PanfluteElementAccumulatorElementFilterContext(Generic[T], ContextManager[Tuple[PanfluteElementFilter, Optional[PanfluteElementPredicate]]]):
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
        return element

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._is_complete = True

    @property
    def result(self) -> T:
        if not self._is_complete:
            raise ValueError("Cannot retrieve accumulated value before walk is complete")

        return self._result

    @staticmethod
    def _execute_accumulator_walk(element: panflute.Element, accumulator_instance: Any) -> T:
        with accumulator_instance as (element_filter, stop_if_actual):
            doc = element if isinstance(element, panflute.Doc) else element.doc
            element.walk(element_filter, doc=doc, stop_if=stop_if_actual)
        return accumulator_instance.result

    @classmethod
    def accumulate_from_elements(cls, element: panflute.Element, accumulator: PanfluteElementAccumulatorFunc, seed: Optional[T] = None, stop_if: Optional[PanfluteElementPredicate] = None) -> T:
        accumulator_instance = cls(accumulator, seed, stop_if)
        return cls._execute_accumulator_walk(element, accumulator_instance)

    @classmethod
    def count_elements(cls, element: panflute.Element, predicate: PanfluteElementPredicate = None) -> int:
        if predicate is None:
            predicate = lambda element, doc: True

        def accumulator_func(element: panflute.Element, _: panflute.Doc, count: int) -> int:
            if predicate(element):
                return count + 1

            return count

        return cls.accumulate_from_elements(element, accumulator=accumulator_func, seed=0, stop_if=None)

    @classmethod
    def any_elements(cls, element: panflute.Element, predicate: PanfluteElementPredicate = None) -> bool:
        if predicate is None:
            predicate = lambda element, doc: True

        stop_now: bool = False
        def accumulator_func(element: panflute.Element, _: panflute.Doc, count: int) -> int:
            if predicate(element):
                nonlocal stop_now
                stop_now = True
                return count + 1

            return count

        return cls.accumulate_from_elements(element, accumulator=accumulator_func, seed=0, stop_if=lambda _: stop_now) > 0

    @classmethod
    def all_elements(cls, element: panflute.Element, predicate: PanfluteElementPredicate = None) -> bool:
        if predicate is None:
            predicate = lambda element, doc: True

        stop_now: bool = False
        def accumulator_func(element: panflute.Element, _: panflute.Doc, count: int) -> int:
            if not predicate(element):
                nonlocal stop_now
                stop_now = True
                return count + 1
            else:
                return count

        return cls.accumulate_from_elements(element, accumulator=accumulator_func, seed=0, stop_if=lambda _: stop_now) == 0
