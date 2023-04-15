import re
from typing import Tuple, overload, Union, Optional

from markdown_dom.AbstractDocumentElementContentText import AbstractDocumentElementContentText


class DocumentElementContentTextMatch:
    """
    A match object is returned by the search() and match() functions. A match object always has a boolean value of True, so you can test if there was a match simply by testing the match object: if match: ... If you want to determine whether the RE matches at the beginning or end of the string, use match() or search() instead.
    """

    def __init__(self, document_element_content_text: AbstractDocumentElementContentText, match: re.Match):
        if not isinstance(document_element_content_text, AbstractDocumentElementContentText):
            raise TypeError(f'document_element_content_text must be an AbstractDocumentElementContentText, not {type(document_element_content_text)}')
        if not isinstance(match, re.Match):
            raise TypeError(f'match must be a re.Match, not {type(match)}')

        self._document_element_content_text = document_element_content_text
        self._match = match

    @overload
    def group(self) -> AbstractDocumentElementContentText:
        """
        Returns one or more subgroups of the match. If there is a single argument, the result is a single string; if there are
        multiple arguments, the result is a tuple with one item per argument. The default argument is 0, which returns the whole match.
        """
        underlying_group_span = self._match.span()
        return self._document_element_content_text.get_slice_by_doc_text_range(
            doc_text_start_index=underlying_group_span[0],
            text_len=underlying_group_span[1]-underlying_group_span[0],
        )

    def group(self, *groups: Union[str, int]) -> Union[AbstractDocumentElementContentText, Tuple[AbstractDocumentElementContentText, ...]]:
        """
        Returns one or more subgroups of the match. If there is a single argument, the result is a single string; if there are
        multiple arguments, the result is a tuple with one item per argument. The default argument is 0, which returns the whole match.
        """
        if len(groups) == 0:
            underlying_group_span = self._match.span()
            return self._document_element_content_text.get_slice_by_doc_text_range(
                doc_text_start_index=underlying_group_span[0],
                text_len=underlying_group_span[1]-underlying_group_span[0],
            )
        elif len(groups) == 1:
            underlying_group_span = self._match.span(groups[0])
            return self._document_element_content_text.get_slice_by_doc_text_range(
                doc_text_start_index=underlying_group_span[0],
                text_len=underlying_group_span[1]-underlying_group_span[0],
            )
        else:
            return tuple(
                self.group(group)
                for group in groups
            )

    def __getitem__(self, *groups: Union[str, int]) -> Union[AbstractDocumentElementContentText, Tuple[AbstractDocumentElementContentText, ...]]:
        """
        Returns one or more subgroups of the match. If there is a single argument, the result is a single string; if there are multiple arguments, the result is a tuple with one item per argument. The default argument is 0, which returns the whole match.
        """
        return self.group(*groups)

    def groupdict(self, group: Optional[Union[int, str]]) -> dict[Union[str, int], AbstractDocumentElementContentText]:
        """
        Returns a dictionary containing all the named subgroups of the match, keyed by the subgroup name. The default
        argument is 0, which returns the whole match.
        """
        underlying_groupdict_keys = self._match.groupdict(group).keys()
        return {
            key: self.group(*(group,))
            for key in underlying_groupdict_keys
        }

    @property
    def start(self) -> int:
        """
        The index of the start of the match, relative to the start of the string.
        """
        return self._match.start()

    @property
    def end(self) -> int:
        """
        The index of the end of the match, relative to the start of the string.
        """
        return self._match.end()

    def __bool__(self):
        """
        Returns True if the match was successful, False otherwise.
        """
        return self._match.__bool__()
