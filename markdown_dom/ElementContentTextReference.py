from typing import Callable, Optional

import panflute

from markdown_dom.AbstractElementContentTextReference import AbstractElementContentTextReference


class ElementContentTextReference(AbstractElementContentTextReference):
    def __init__(self,
                 element: panflute.Element,
                 get_content_text: Callable[[panflute.Element], str],
                 get_content_text_len: Callable[[panflute.Element], int],
                 replace_content_text_completely: Optional[Callable[[panflute.Element, str], None]] = None,
                 replace_content_text_partially: Optional[Callable[[panflute.Element, int, int, str], None]] = None,
                 delete_content_text_completely: Optional[Callable[[panflute.Element], None]] = None,
                 delete_content_text_partially: Optional[Callable[[panflute.Element, int, int], None]] = None,
                 insert_content_text: Optional[Callable[[panflute.Element, int, str], None]] = None,
                 ):
        self._element = element
        self._get_content_text = get_content_text
        self._get_content_text_len = get_content_text_len
        self._replace_content_text_completely = replace_content_text_completely

        if replace_content_text_completely:
            def replace_content_text_partially_via_replace(element: panflute.Element, start_index: int, end_index: int, repl: str) -> None:
                new_text_content = self.text[:start_index] + repl + self.text[end_index:]
                self._replace_content_text_completely(element, new_text_content)

            def delete_content_text_completely_via_replace(element: panflute.Element) -> None:
                new_text_content = ""
                self._replace_content_text_completely(element, new_text_content)

            def delete_content_text_partially_via_replace(element: panflute.Element, start_index: int, end_index: int) -> None:
                new_text_content = self.text[:start_index] + self.text[end_index:]
                self._replace_content_text_completely(element, new_text_content)

            def insert_content_text_via_replace(element: panflute.Element, start_index: int, repl: str) -> None:
                new_text_content = self.text[:start_index] + repl + self.text[start_index:]
                self._replace_content_text_completely(element, new_text_content)

            replace_content_text_partially = replace_content_text_partially or replace_content_text_partially_via_replace
            delete_content_text_completely = delete_content_text_completely or delete_content_text_completely_via_replace
            delete_content_text_partially = delete_content_text_partially or delete_content_text_partially_via_replace
            insert_content_text = insert_content_text or insert_content_text_via_replace

        self._delete_content_text_partially = delete_content_text_partially
        self._delete_content_text_completely = delete_content_text_completely
        self._replace_content_text_partially = replace_content_text_partially
        self._insert_content_text = insert_content_text

    @property
    def element(self) -> panflute.Element:
        return self._element

    @property
    def text(self) -> str:
        return self._get_content_text(self.element)

    @property
    def text_len(self) -> int:
        return self._get_content_text_len(self.element)

    @property
    def supports_text_partial_delete(self) -> bool:
        return self._delete_content_text_partially is not None

    def delete_text(self, start_index: int, end_index: int) -> None:
        self._delete_content_text_partially(self.element, start_index, end_index)

    @property
    def supports_text_complete_delete(self) -> bool:
        return self._delete_content_text_completely is not None

    def delete_text_completely(self) -> None:
        self._delete_content_text_completely(self.element)

    @property
    def supports_text_partial_replace(self) -> bool:
        return self._replace_content_text_partially is not None

    def replace_text(self, start_index: int, end_index: int, repl: str) -> None:
        self._replace_content_text_partially(self.element, start_index, end_index, repl)

    @property
    def supports_text_completely_replace(self) -> bool:
        return self._replace_content_text_completely is not None

    def replace_text_completely(self, repl: str) -> None:
        self._replace_content_text_completely(self.element, repl)

    @property
    def supports_text_insert(self) -> bool:
        return self._insert_content_text is not None

    def insert_text(self, start_index: int, repl: str) -> None:
        self._insert_content_text(self.element, start_index, repl)


