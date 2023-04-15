import re

from typing import Iterable, Callable, Optional, List, Any, Union

from markdown_dom.MarkdownDocument import MarkdownDocument
from markdown_dom.AbstractDocumentElementContentText import AbstractDocumentElementContentText
from markdown_dom.CompoundDocumentElementContentTextMap import CompoundDocumentElementContentTextMap
from markdown_re.DocumentElementContentTextMatch import DocumentElementContentTextMatch
from markdown_re.type_variables import T, PatternLike, PanfluteElementLike, normalize_elementlike


class MarkdownDocumentTextPattern:
    """
    A compiled representation of a regular expression intended to be run against a MarkdownDocument's plaintext.
    This object stores the pattern and the flags that were passed to compile().
    """

    def __init__(self, pattern: PatternLike, flags: Optional[re.RegexFlag] = None):
        """
        Compile a regular expression pattern, returning a pattern object. The expression’s behaviour can be modified by
        specifying a flags value.
        :param pattern: The regular expression pattern to be compiled.
        :param flags: A bitwise OR of the flags.
        """

        if isinstance(pattern, MarkdownDocumentTextPattern):
            if flags is not None:
                raise ValueError("Cannot specify flags when pattern is already a MarkdownDocumentTextPattern")
            self._pattern = pattern._pattern
        if isinstance(pattern, re.Pattern):
            if flags is not None:
                raise ValueError("Cannot specify flags when pattern is already a MarkdownDocumentTextPattern")
            self._pattern = pattern
        self._pattern = re.compile(pattern, flags=flags)

    def match(self,
              doc: MarkdownDocument,
              action: Callable[[Optional[DocumentElementContentTextMatch]], T] = lambda m: m,
              pos: Optional[int] = None,
              endpos: Optional[int] = None,
              action_is_readonly: bool = True,
              ) -> T:
        """
        Try to apply the pattern at the start of the MarkdownDocument's plaintext, returning a match object, or None if no
        match was found.
        :param doc: The MarkdownDocument to match against.
        :param action: A function to apply to the match object, if one is found. The function should take a single argument, which will be the match object, and return a value of type T.
        :param pos: The position in the string where the search is to start.
        :param endpos: The position in the string where the search is to end.
        :param action_is_readonly: Whether the document should be treated as read-only while action is running.
        :return: A value of type T, as determined by the action function.
        """

        def action_wrapper(text_map_generator: Iterable[AbstractDocumentElementContentText]) -> T:
            text_map: AbstractDocumentElementContentText = next(text_map_generator)
            inner_match_kwargs = {}
            if pos is not None:
                inner_match_kwargs['pos'] = pos
            if endpos is not None:
                inner_match_kwargs['endpos'] = endpos
            underlying_match = self._pattern.match(text_map.text, **inner_match_kwargs)
            mapped_match = DocumentElementContentTextMatch(text_map, underlying_match) if underlying_match else None
            return action(mapped_match)

        return doc.use_text_content(action_wrapper, readonly=action_is_readonly)

    def search(self,
               doc: MarkdownDocument,
               action: Callable[[Optional[DocumentElementContentTextMatch]], T] = lambda m: m,
               pos: Optional[int] = None,
               endpos: Optional[int] = None,
               action_is_readonly: bool = True,
               ) -> T:
        """
        Scan through the MarkdownDocument's plaintext looking for a match, and return a match object, or None if no match
        was found.
        :param doc: The MarkdownDocument to match against.
        :param action: The action to take on the match.
        :param pos: The position in the string where the search is to start.
        :param endpos: The position in the string where the search is to end.
        :param action_is_readonly: Whether the document should be treated as read-only while action is running.
        :return: A value of type T, as determined by the action function.
        """

        def action_wrapper(text_map_generator: Iterable[AbstractDocumentElementContentText]) -> T:
            text_map: AbstractDocumentElementContentText = next(text_map_generator)
            inner_search_kwargs = {}
            if pos is not None:
                inner_search_kwargs['pos'] = pos
            if endpos is not None:
                inner_search_kwargs['endpos'] = endpos
            underlying_match = self._pattern.search(text_map.text, **inner_search_kwargs)
            mapped_match = DocumentElementContentTextMatch(text_map, underlying_match) if underlying_match else None
            return action(mapped_match)

        return doc.use_text_content(action_wrapper, readonly=action_is_readonly)

    def fullmatch(self,
                  doc: MarkdownDocument,
                  action: Callable[[Optional[DocumentElementContentTextMatch]], T] = lambda m: m,
                  pos: Optional[int] = None,
                  endpos: Optional[int] = None,
                  action_is_readonly: bool = True,
                  ) -> T:
        """
        Try to apply the pattern to the entirety of the MarkdownDocument's plaintext, returning a match object,
        or None if no match was found.
        :param doc: The MarkdownDocument to match against.
        :param action: The action to take on the match.
        :param pos: The position in the string where the search is to start.
        :param endpos: The position in the string where the search is to end.
        :param action_is_readonly: Whether the document should be treated as read-only while action is running.
        :return: A value of type T, as determined by the action function.
        """

        def action_wrapper(text_map_generator: Iterable[AbstractDocumentElementContentText]) -> T:
            text_map: AbstractDocumentElementContentText = next(text_map_generator)
            inner_fullmatch_kwargs = {}
            if pos is not None:
                inner_fullmatch_kwargs['pos'] = pos
            if endpos is not None:
                inner_fullmatch_kwargs['endpos'] = endpos
            underlying_match = self._pattern.fullmatch(text_map.text, **inner_fullmatch_kwargs)
            mapped_match = DocumentElementContentTextMatch(text_map, underlying_match) if underlying_match else None
            return action(mapped_match)

        return doc.use_text_content(action_wrapper, readonly=action_is_readonly)

    def findall(self,
                doc: MarkdownDocument,
                action: Callable[[List[Any]], T] = lambda m: m,
                pos: Optional[int] = None,
                endpos: Optional[int] = None,
                ) -> T:
        """
        Return a list of all non-overlapping matches in the MarkdownDocument's plaintext.
        :param doc: The MarkdownDocument to match against.
        :param action: The action to take on the match.
        :param pos: The position in the string where the search is to start.
        :param endpos: The position in the string where the search is to end.
        :return: A value of type T, as determined by the action function.
        """

        def action_wrapper(text_map_generator: Iterable[AbstractDocumentElementContentText]) -> T:
            text_map: AbstractDocumentElementContentText = next(text_map_generator)
            inner_findall_kwargs = {}
            if pos is not None:
                inner_findall_kwargs['pos'] = pos
            if endpos is not None:
                inner_findall_kwargs['endpos'] = endpos
            found_texts: List[Any] = self._pattern.findall(text_map.text, **inner_findall_kwargs)
            return action(found_texts)

        return doc.use_text_content(action_wrapper, readonly=True)

    def finditer(self,
                 doc: MarkdownDocument,
                 action: Callable[[Iterable[DocumentElementContentTextMatch]], T] = lambda m: m,
                 pos: Optional[int] = None,
                 endpos: Optional[int] = None,
                 action_is_readonly: bool = True,
                 ) -> T:
        """
        Return an iterator over all non-overlapping matches in the MarkdownDocument's plaintext.
        :param doc: The MarkdownDocument to match against.
        :param action: The action to take on the match.
        :param pos: The position in the string where the search is to start.
        :param endpos: The position in the string where the search is to end.
        :param action_is_readonly: Whether the document should be treated as read-only while action is running.
        :return: A value of type T, as determined by the action function.
        """

        def action_wrapper(text_map_generator: Iterable[AbstractDocumentElementContentText]) -> T:
            text_map: AbstractDocumentElementContentText = next(text_map_generator)
            inner_finditer_kwargs = {}
            if pos is not None:
                inner_finditer_kwargs['pos'] = pos
            if endpos is not None:
                inner_finditer_kwargs['endpos'] = endpos
            underlying_matches = self._pattern.finditer(text_map.text, **inner_finditer_kwargs)
            mapped_matches = (DocumentElementContentTextMatch(text_map, m) for m in underlying_matches)
            return action(mapped_matches)

        return doc.use_text_content(action_wrapper, readonly=action_is_readonly)

    def sub(self,
            doc: MarkdownDocument,
            repl: Union[PanfluteElementLike, Callable[[DocumentElementContentTextMatch], PanfluteElementLike]],
            pos: Optional[int] = None,
            endpos: Optional[int] = None,
            ) -> None:
        """
        Update the MarkdownDocument's plaintext to reflect the string obtained by replacing the leftmost non-overlapping
        occurrences of pattern in the MarkdownDocument's plaintext by the replacement repl.
        :param doc: The MarkdownDocument to match against.
        :param repl: The replacement string.
        :param pos: The position in the string where the search is to start.
        :param endpos: The position in the string where the search is to end.
        :return: A value of type T, as determined by the action function.
        """

        if repl == '':
            return self.rm(doc, pos=pos, endpos=endpos)

        if repl is None:
            raise ValueError("repl cannot be None")

        if not callable(repl):
            repl = lambda match: repl

        def action_wrapper(text_map_generator: Iterable[AbstractDocumentElementContentText]) -> None:
            text_map: AbstractDocumentElementContentText = next(text_map_generator)
            inner_finditer_kwargs = {}
            if pos is not None:
                inner_finditer_kwargs['pos'] = pos
            if endpos is not None:
                inner_finditer_kwargs['endpos'] = endpos
            next_underlying_match = next(self._pattern.finditer(text_map.text, **inner_finditer_kwargs), None)

            while next_underlying_match is not None:
                mapped_match = DocumentElementContentTextMatch(text_map, next_underlying_match)
                replacement = normalize_elementlike(repl(mapped_match))
                replacement_text_len = CompoundDocumentElementContentTextMap.from_element_walk(replacement).text_len
                text_map.replace_slice_by_doc_text_range(mapped_match.start, mapped_match.end - mapped_match.start, replacement)

                text_map = next(text_map_generator)
                inner_finditer_kwargs['pos'] = mapped_match.start + replacement_text_len
                next_underlying_match = next(self._pattern.finditer(text_map.text, **inner_finditer_kwargs), None)

        doc.use_text_content(action_wrapper, readonly=False)

    def rm(self,
           doc: MarkdownDocument,
           pos: Optional[int] = None,
           endpos: Optional[int] = None,
           ) -> None:
        """
        Update the MarkdownDocument's plaintext to reflect the string obtained by removing the leftmost non-overlapping
        occurrences of pattern in the MarkdownDocument's plaintext.
        :param doc: The MarkdownDocument to match against.
        :param pos: The position in the string where the search is to start.
        :param endpos: The position in the string where the search is to end.
        """

        def action_wrapper(text_map_generator: Iterable[AbstractDocumentElementContentText]) -> None:
            text_map: AbstractDocumentElementContentText = next(text_map_generator)

            inner_finditer_kwargs = {}
            if pos is not None:
                inner_finditer_kwargs['pos'] = pos
            if endpos is not None:
                inner_finditer_kwargs['endpos'] = endpos

            next_underlying_match = next(self._pattern.finditer(text_map.text, **inner_finditer_kwargs), None)

            while next_underlying_match is not None:
                mapped_match = DocumentElementContentTextMatch(text_map, next_underlying_match)
                text_map.remove_slice_by_doc_text_range(mapped_match.start, mapped_match.end - mapped_match.start)

                text_map = next(text_map_generator)
                inner_finditer_kwargs['pos'] = mapped_match.start
                next_underlying_match = next(self._pattern.finditer(text_map.text, **inner_finditer_kwargs), None)

        doc.use_text_content(action_wrapper, readonly=False)
