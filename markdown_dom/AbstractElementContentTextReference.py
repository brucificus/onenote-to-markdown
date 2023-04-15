from abc import ABCMeta, abstractmethod

import panflute


class AbstractElementContentTextReference(metaclass=ABCMeta):
    @property
    @abstractmethod
    def element(self) -> panflute.Element:
        raise NotImplementedError()

    @property
    @abstractmethod
    def text(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def text_len(self) -> int:
        raise NotImplementedError()

    @property
    @abstractmethod
    def supports_text_partial_delete(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def delete_text(self, start_index: int, end_index: int) -> None:
        raise NotImplementedError()

    @property
    @abstractmethod
    def supports_text_complete_delete(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def delete_text_completely(self) -> None:
        raise NotImplementedError()

    @property
    @abstractmethod
    def supports_text_partial_replace(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def replace_text(self, start_index: int, end_index: int, repl: str) -> None:
        raise NotImplementedError()

    @property
    @abstractmethod
    def supports_text_completely_replace(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def replace_text_completely(self, repl: str) -> None:
        raise NotImplementedError()

    @property
    @abstractmethod
    def supports_text_insert(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def insert_text(self, start_index: int, repl: str) -> None:
        raise NotImplementedError()

