import itertools

from typing import Tuple, Callable, Iterable, Sized, Sequence

import panflute

from markdown_dom.AbstractDocumentElementContentText import AbstractDocumentElementContentText
from markdown_dom.AbstractElementContentTextReference import AbstractElementContentTextReference
from markdown_dom.DocumentElementContentTextMapEntry import DocumentElementContentTextMapEntry
from markdown_dom._yield_document_order_element_content_text_references import \
    _yield_document_order_element_content_text_references
from markdown_dom.type_variables import PanfluteElementLike


_SliceDef = Tuple[
    Tuple[AbstractDocumentElementContentText,Tuple[int, int]],
    Sequence[AbstractDocumentElementContentText],
    Tuple[AbstractDocumentElementContentText, Tuple[int, int]]
]


class CompoundDocumentElementContentTextMap(AbstractDocumentElementContentText):
    def __init__(self, yield_element_content_text_references: Callable[[], Iterable[AbstractElementContentTextReference]]):
        self._yield_element_content_text_references = yield_element_content_text_references
        self._doc_text_start_index: int = 0
        self._text = None
        self._text_len = None
        self._items: Tuple[AbstractDocumentElementContentText, ...] = None

    def _build_items_if_needed(self):
        if self._items is not None:
            return

        self._items = ()
        self._text_len = 0

        for element_text_reference in self._yield_element_content_text_references():
            doc_text_start_index = self._doc_text_start_index + self._text_len
            self._text_len += element_text_reference.text_len
            self._items += (DocumentElementContentTextMapEntry(
                doc_text_start_index=doc_text_start_index,
                element_text_reference=element_text_reference,
            ),)

    def _build_text_if_needed(self):
        if self._text is not None:
            return
        self._build_items_if_needed()
        self._text = ''.join(i.text for i in self._items)
        assert len(self._text) == self._text_len

    @property
    def elements(self) -> Iterable[panflute.Element]:
        self._build_items_if_needed()
        for i in self._items:
            yield from i.elements

    @classmethod
    def from_element_walk(cls, source: PanfluteElementLike) -> AbstractDocumentElementContentText:
        return cls(lambda: _yield_document_order_element_content_text_references(source))

    @classmethod
    def from_element_content_text_references(cls, items: Iterable[AbstractElementContentTextReference], doc_text_start_index: int = 0) -> AbstractDocumentElementContentText:
        if isinstance(items, Sized):
            if len(items) == 0:
                raise ValueError('items must not be empty')
            if len(items) == 1:
                single_item = next(iter(items))
                return DocumentElementContentTextMapEntry(
                    doc_text_start_index=doc_text_start_index,
                    element_text_reference=single_item,
                )
        return cls(lambda: items, doc_text_start_index=doc_text_start_index)

    @classmethod
    def from_map_entries(cls, map_entries: Iterable[DocumentElementContentTextMapEntry]) -> AbstractDocumentElementContentText:
        if isinstance(map_entries, Sized):
            if len(map_entries) == 0:
                raise ValueError('items must not be empty')
            if len(map_entries) == 1:
                single_map_entry = next(iter(map_entries))
                return single_map_entry

        result = cls(lambda: ())
        result._doc_text_start_index = map_entries[0].doc_text_start_index
        result._text = None
        result._items = tuple(map_entries)
        result._text_len = sum(i.text_len for i in result._items)
        return result

    @property
    def doc_text_start_index(self) -> int:
        return self._doc_text_start_index

    @property
    def text(self) -> str:
        self._build_text_if_needed()
        return self._text

    @property
    def text_len(self) -> int:
        self._build_items_if_needed()
        return self._text_len

    def _slice_impl(self, doc_text_start_index: int, text_len: int) -> _SliceDef:
        self._build_items_if_needed()

        if doc_text_start_index < 0:
            raise ValueError(f'text_start_index must be >= 0, received {doc_text_start_index}')
        if text_len <= 0:
            raise ValueError(f'text_len must be > 0, received {text_len}')
        if doc_text_start_index + text_len > self._doc_text_start_index + self._text_len:
            raise ValueError(f'text_start_index + text_len must be <= {self._doc_text_start_index + self._text_len}, received {doc_text_start_index + text_len}')

        self._build_text_if_needed()

        def ends_before_start_of_first_element(i: AbstractDocumentElementContentText):
            return i.doc_text_start_index + i.text_len <= doc_text_start_index

        def starts_before_end_of_last_element(i: AbstractDocumentElementContentText):
            return i.doc_text_start_index < doc_text_start_index + text_len

        result_items = itertools.dropwhile(ends_before_start_of_first_element, self._items)
        result_items = itertools.takewhile(starts_before_end_of_last_element, result_items)
        result_items = tuple(result_items)

        if len(result_items) == 0:
            raise ValueError(f'No items found for text_start_index={doc_text_start_index}, text_len={text_len}')

        first_item = result_items[0]
        if len(result_items) == 1:
            return first_item.get_slice_by_doc_text_range(doc_text_start_index, text_len)

        first_item_slice_doc_text_start_index = doc_text_start_index
        first_item_slice_text_len = first_item.text_len - (first_item_slice_doc_text_start_index - first_item.doc_text_start_index)

        middle_items = result_items[1:-1] if len(result_items) >= 3 else ()
        middle_items_text_len_sum = sum(i.text_len for i in middle_items)

        nonlast_items_text_len_sum = first_item_slice_text_len + middle_items_text_len_sum

        last_item = result_items[-1]
        last_item_slice_len = text_len - nonlast_items_text_len_sum

        return ((first_item, (first_item_slice_doc_text_start_index, first_item_slice_text_len)),
                middle_items,
                (last_item, (last_item.doc_text_start_index, last_item_slice_len)))

    def get_slice_by_doc_text_range(self, doc_text_start_index: int, text_len: int) -> AbstractDocumentElementContentText:
        slice_def = self._slice_impl(doc_text_start_index, text_len)

        (first_item, (first_item_slice_doc_text_start_index, first_item_slice_text_len)) = slice_def[0]
        middle_items = slice_def[1]
        (last_item, (last_item_doc_text_start_index, last_item_slice_len)) = slice_def[2]

        first_item_sliced = first_item.get_slice_by_doc_text_range(first_item_slice_doc_text_start_index, first_item_slice_text_len)
        last_item_sliced = last_item.get_slice_by_doc_text_range(last_item.doc_text_start_index, last_item_slice_len)

        return self.from_map_entries((first_item_sliced, *middle_items, last_item_sliced))

    def remove_slice_by_doc_text_range(self, doc_text_start_index: int, text_len: int) -> None:
        slice_def = self._slice_impl(doc_text_start_index, text_len)

        (first_item, (first_item_slice_doc_text_start_index, first_item_slice_text_len)) = slice_def[0]
        middle_items = slice_def[1]
        (last_item, (last_item_doc_text_start_index, last_item_slice_len)) = slice_def[2]

        if first_item_slice_text_len == first_item.text_len:
            middle_items = (first_item, *middle_items)
            first_item_sliced = None
        else:
            first_item_sliced = first_item.get_slice_by_doc_text_range(first_item_slice_doc_text_start_index, first_item_slice_text_len)

        if last_item_slice_len == last_item.text_len:
            middle_items = (*middle_items, last_item)
        else:
            last_item_sliced = last_item.get_slice_by_doc_text_range(last_item_doc_text_start_index, last_item_slice_len)
            last_item_sliced.remove_slice_by_doc_text_range(last_item_doc_text_start_index, last_item_slice_len)

        for text_map_entry in reversed(middle_items):
            # We don't need to directly track and cleanup updated parents because that is handled by the leaf implementation.
            text_map_entry.remove_slice_by_doc_text_range(text_map_entry.doc_text_start_index, text_map_entry.text_len)

        if first_item_sliced is not None:
            first_item_sliced.remove_slice_by_doc_text_range(first_item_slice_doc_text_start_index, first_item_slice_text_len)

    def replace_slice_by_doc_text_range(self, doc_text_start_index: int, text_len: int, repl: PanfluteElementLike) -> None:
        raise NotImplementedError()
