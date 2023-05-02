from typing import Iterable, Tuple

import panflute

from markdown_dom.AbstractDocumentElementContentText import AbstractDocumentElementContentText
from markdown_dom.AbstractElementContentTextReference import AbstractElementContentTextReference
from markdown_dom.SlicedElementContentTextReference import SlicedElementContentTextReference
from markdown_dom.type_variables import PanfluteElementLike


_SliceDef = Tuple[int, int]


class DocumentElementContentTextMapEntry(AbstractDocumentElementContentText):
    def __init__(self, doc_text_start_index: int, element_text_reference: AbstractElementContentTextReference):
        self._doc_text_start_index = doc_text_start_index
        self._element_text_reference = element_text_reference

    @property
    def doc_text_start_index(self) -> int:
        return self._doc_text_start_index

    @property
    def text(self) -> int:
        return self._element_text_reference.text

    @property
    def text_len(self) -> int:
        return self._element_text_reference.text_len

    @property
    def elements(self) -> Iterable[panflute.Element]:
        yield self._element_text_reference.element

    def get_slice_by_doc_text_range(self, doc_text_start_index: int, text_len: int) -> AbstractDocumentElementContentText:
        if doc_text_start_index < 0:
            raise ValueError(f'text_start_index must be >= 0, received {doc_text_start_index}')
        if text_len <= 0:
            raise ValueError(f'text_len must be > 0, received {text_len}')
        if doc_text_start_index < self._doc_text_start_index:
            raise ValueError(f'doc_text_start_index must be >= {self._doc_text_start_index}, received {doc_text_start_index}')
        if doc_text_start_index + text_len > self._doc_text_start_index + len(self):
            raise ValueError(f'doc_text_start_index + text_len must be <= {self._doc_text_start_index + len(self)}, received {doc_text_start_index + text_len}')

        if doc_text_start_index == 0 and text_len == len(self):
            return self

        return DocumentElementContentTextMapEntry(
            doc_text_start_index=self._doc_text_start_index + doc_text_start_index,
            element_text_reference=SlicedElementContentTextReference(
                adapted=self._element_text_reference,
                slice_start=doc_text_start_index - self._doc_text_start_index,
                slice_len=text_len,
        ),)

    def remove_slice_by_doc_text_range(self, doc_text_start_index: int, text_len: int) -> None:
        if doc_text_start_index < 0:
            raise ValueError(f'text_start_index must be >= 0, received {doc_text_start_index}')
        if text_len <= 0:
            raise ValueError(f'text_len must be > 0, received {text_len}')
        if doc_text_start_index < self._doc_text_start_index:
            raise ValueError(f'doc_text_start_index must be >= {self._doc_text_start_index}, received {doc_text_start_index}')
        if doc_text_start_index + text_len > self._doc_text_start_index + len(self):
            raise ValueError(
                f'doc_text_start_index + text_len must be <= {self._doc_text_start_index + len(self)}, received {doc_text_start_index + text_len}')

        if doc_text_start_index != self._doc_text_start_index or text_len != self.text_len:
            # Partial removal.
            self._element_text_reference.delete_text(doc_text_start_index - self._doc_text_start_index, text_len)
            return

        updated_parents = ()

        element = self._element_text_reference.element
        element_parent = element.parent
        if element_parent is not None:
            updated_parents += (element_parent,)
        self._element_text_reference.delete_text_completely()

        parent_types_useless_when_empty = (
            panflute.Para, panflute.BlockQuote, panflute.Emph, panflute.Strong, panflute.Strikeout, panflute.SmallCaps,
            panflute.Superscript, panflute.Subscript, panflute.Span, panflute.Header, panflute.Div, panflute.Quoted,
            panflute.ListItem, panflute.OrderedList, panflute.BulletList, panflute.LineItem, panflute.LineBlock,
            panflute.Caption,
        )

        while len(updated_parents) > 0:
            for parent in list(updated_parents):
                updated_parents = updated_parents[1:]
                if len(parent.content) == 0:
                    if isinstance(parent, parent_types_useless_when_empty):
                        if parent.parent is not None:
                            if parent.parent not in updated_parents:
                                updated_parents += (parent.parent,)
                            parent.parent.content.remove(parent)

    def replace_slice_by_doc_text_range(self, doc_text_start_index: int, text_len: int, repl: PanfluteElementLike) -> None:
        raise NotImplementedError()
