from abc import ABC, abstractmethod
from typing import Optional

import panflute

from markdown_dom.type_variables import PanfluteElementPredicate, PanfluteElementFilter, PanfluteElementLike


class AbstractPanfluteElementPredicateFilterPair(PanfluteElementFilter, ABC):
    @property
    @abstractmethod
    def element_predicate(self) -> PanfluteElementPredicate:
        raise NotImplementedError()

    @property
    @abstractmethod
    def element_filter(self) -> PanfluteElementFilter:
        raise NotImplementedError()

    @property
    @abstractmethod
    def description(self) -> str:
        if hasattr(self.element_predicate, "__name__") and hasattr(self.element_filter, "__name__"):
            return f"{self.element_predicate.__name__} -> {self.element_filter.__name__}"
        if self.element_predicate and self.element_filter:
            return f"{self.element_predicate} -> {self.element_filter}"
        raise NotImplementedError()

    def __call__(self, element: panflute.Element, doc: panflute.Doc) -> Optional[PanfluteElementLike]:
        if self.element_predicate(element):
            return self.element_filter(element, doc)
        return element


class PanfluteElementPredicateFilterPair(AbstractPanfluteElementPredicateFilterPair):
    def __init__(self, element_predicate: PanfluteElementPredicate, element_filter: PanfluteElementFilter, description: Optional[str] = None):
        self._element_predicate = element_predicate
        self._element_filter = element_filter
        if description:
            self._description = description
        elif hasattr(self.element_predicate, "__name__") and hasattr(self.element_filter, "__name__"):
            self._description = f"{self.element_predicate.__name__} -> {self.element_filter.__name__}"
        elif self.element_predicate and self.element_filter:
            self._description = f"{self.element_predicate} -> {self.element_filter}"

    @property
    def element_predicate(self) -> PanfluteElementPredicate:
        return self._element_predicate

    @property
    def element_filter(self) -> PanfluteElementFilter:
        return self._element_filter

    @property
    def description(self) -> str:
        return self._description
