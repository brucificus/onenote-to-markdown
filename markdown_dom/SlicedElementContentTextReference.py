import panflute

from markdown_dom.AbstractElementContentTextReference import AbstractElementContentTextReference


class SlicedElementContentTextReference(AbstractElementContentTextReference):
    def __init__(self, adapted: AbstractElementContentTextReference, slice_start: int, slice_len: int):
        if slice_start == 0 and slice_len == adapted.text_len:
            raise ValueError('Not valid to make a slice representing the whole original')

        if not isinstance(adapted, SlicedElementContentTextReference):
            self._adapted = adapted
            self._slice_start = slice_start
            self._slice_len = slice_len
        else:
            self._adapted = adapted._adapted
            self._slice_start = adapted._slice_start + slice_start
            self._slice_len = slice_len

    @property
    def element(self) -> panflute.Element:
        return self._adapted.element

    @property
    def text(self) -> str:
        return self._adapted.text[self._slice_start:self._slice_start + self._slice_len]

    @property
    def text_len(self) -> int:
        return self._slice_len

    @property
    def supports_text_partial_delete(self) -> bool:
        return self._adapted.supports_text_partial_delete

    def delete_text(self, start_index: int, end_index: int) -> None:
        if start_index < 0 or start_index > self._slice_len:
            raise ValueError('start_index out of range')
        if end_index < 0 or end_index > self._slice_len:
            raise ValueError('end_index out of range')

        self._adapted.delete_text(self._slice_start + start_index, self._slice_start + end_index)
        self._slice_len -= end_index - start_index

    @property
    def supports_text_complete_delete(self) -> bool:
        return self._adapted.supports_text_complete_delete

    def delete_text_completely(self) -> None:
        self._adapted.delete_text_completely()
        self._slice_len = 0

    @property
    def supports_text_partial_replace(self) -> bool:
        return self._adapted.supports_text_partial_replace

    def replace_text(self, start_index: int, end_index: int, repl: str) -> None:
        if start_index < 0 or start_index > self._slice_len:
            raise ValueError('start_index out of range')
        if end_index < 0 or end_index > self._slice_len:
            raise ValueError('end_index out of range')

        self._adapted.replace_text(self._slice_start + start_index, self._slice_start + end_index, repl)
        self._slice_len += len(repl) - (end_index - start_index)

    @property
    def supports_text_completely_replace(self) -> bool:
        return self._adapted.supports_text_completely_replace

    def replace_text_completely(self, repl: str) -> None:
        self._adapted.content_text = self._adapted.text[:self._slice_start] \
                                     + repl \
                                     + self._adapted.text[self._slice_start + self._slice_len:]
        self._slice_len = len(repl)

    @property
    def supports_text_insert(self) -> bool:
        return self._adapted.supports_text_insert

    def insert_text(self, start_index: int, repl: str) -> None:
        if start_index < 0 or start_index > self._slice_len:
            raise ValueError('start_index out of range')

        self._adapted.insert_text(self._slice_start + start_index, repl)
        self._slice_len += len(repl)

