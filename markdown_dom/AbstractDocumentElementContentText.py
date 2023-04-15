import abc

from typing import Sized, Iterable

import panflute

from markdown_dom.type_variables import PanfluteElementLike


class AbstractDocumentElementContentText(Sized, metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def doc_text_start_index(self) -> int:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def text(self) -> str:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def text_len(self) -> int:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def elements(self) -> Iterable[panflute.Element]:
        raise NotImplementedError()

    @property
    def doc_text_end_index(self) -> int:
        return self.doc_text_start_index + self.text_len

    @abc.abstractmethod
    def get_slice_by_doc_text_range(self, doc_text_start_index: int, text_len: int) -> 'AbstractDocumentElementContentText':
        raise NotImplementedError()

    def __len__(self):
        return self.text_len

    def __str__(self):
        return self.text

    def __repr__(self):
        return f'{self.__class__.__name__}({self.doc_text_start_index!r}, {self.text!r}, {self.elements!r})'

    @abc.abstractmethod
    def remove_slice_by_doc_text_range(self, doc_text_start_index: int, text_len: int) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def replace_slice_by_doc_text_range(self, doc_text_start_index: int, text_len: int, repl: PanfluteElementLike) -> None:
        raise NotImplementedError()
