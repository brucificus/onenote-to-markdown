from abc import ABC, abstractmethod
from typing import Optional, Iterable

import panflute

from markdown_dom.type_variables import PanfluteElementPredicate, PanfluteElementFilter, PanfluteElementLike
from onenote_export.page_export_tasks._element_predicates import PanfluteElementPredicateDescription


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


class PanfluteElementPredicateFilterPairBase(AbstractPanfluteElementPredicateFilterPair, ABC):
    def __init__(self, *, base_elements_predicate):
        self.__base_elements_predicate = base_elements_predicate

    @property
    def __element_predicate_clauses(self) -> Iterable[PanfluteElementPredicate]:
        if self._base_elements_predicate:
            yield self._base_elements_predicate
        yield from self._remaining_element_predicate_clauses

    @property
    def element_predicate(self) -> PanfluteElementPredicate:
        def element_is_match(element: panflute.Element) -> bool:
            return all(element_predicate_clause(element) for element_predicate_clause in self.__element_predicate_clauses)
        return element_is_match

    @property
    def element_filter(self) -> PanfluteElementFilter:
        return self._element_filter

    @property
    def description(self) -> str:
        base_elements_description_prefix = f"{self._base_elements_description} -> " if self._base_elements_description else ""
        return f"{self._description_emoji_infix} {base_elements_description_prefix}{self._describe_remaining_element_predicate_clauses} -> {self._describe_element_filter}"

    @property
    def _base_elements_predicate(self) -> Optional[PanfluteElementPredicate]:
        return self.__base_elements_predicate

    @property
    def _base_elements_description(self) -> Optional[str]:
        if not self._base_elements_predicate:
            return None
        return PanfluteElementPredicateDescription.read_from(self._base_elements_predicate)

    @property
    @abstractmethod
    def _remaining_element_predicate_clauses(self) -> Iterable[PanfluteElementPredicate]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def _describe_remaining_element_predicate_clauses(self) -> Optional[str]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def _element_filter(self) -> PanfluteElementFilter:
        raise NotImplementedError()

    @property
    @abstractmethod
    def _describe_element_filter(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def _description_emoji_infix(self) -> str:
        raise NotImplementedError()


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
