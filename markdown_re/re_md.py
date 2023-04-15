import re

from typing import Iterable, Optional, List, Any, Union, Callable

from markdown_dom.MarkdownDocument import MarkdownDocument
from markdown_re.DocumentElementContentTextMatch import DocumentElementContentTextMatch
from markdown_re.MarkdownDocumentTextPattern import MarkdownDocumentTextPattern
from markdown_re.type_variables import PatternLike, PanfluteElementLike, T


MarkdownPatternLike = Union[MarkdownDocumentTextPattern, PatternLike]


def compile(pattern: PatternLike, flags: Optional[re.RegexFlag] = None) -> MarkdownDocumentTextPattern:
    """
    Compile a regular expression pattern intended to be run against a MarkdownDocument's plaintext, returning a pattern object.
    The expression's behaviour can be modified by specifying a flags value.
    :param pattern: The regular expression pattern to compile.
    :param flags: A bitwise OR of the re module's flags.
    :return: A MarkdownDocumentTextPattern object.
    """

    if isinstance(pattern, MarkdownDocumentTextPattern):
        if flags is not None:
            raise ValueError("Cannot specify flags when pattern is already a MarkdownDocumentTextPattern")
        return pattern
    return MarkdownDocumentTextPattern(pattern, flags=flags)


def match(pattern: MarkdownPatternLike,
          doc: MarkdownDocument,
          action: Callable[[Optional[DocumentElementContentTextMatch]], T] = lambda m: m,
          pos: Optional[int] = None,
          endpos: Optional[int] = None,
          action_is_readonly: bool = True,
          flags: Optional[re.RegexFlag] = None,
          ) -> T:
    """
    Try to apply the pattern to the string of the MarkdownDocument's plaintext, returning a match object, or None if no match was found.
    :param pattern: The regular expression pattern to use. If this is a MarkdownDocumentTextPattern, it will be used as-is. Otherwise, it will be compiled into a MarkdownDocumentTextPattern.
    :param doc: The MarkdownDocument to match against.
    :param action: A function to apply to the match object, if one is found. The function should take a single argument, which will be the match object, and return a value of type T.
    :param pos: The position at which to start matching; defaults to the beginning of the string.
    :param endpos: The position at which to end matching; defaults to the end of the string.
    :param action_is_readonly: Whether the document should be treated as read-only while action is running.
    :param flags: A bitwise OR of the flags.
    """

    pattern = compile(pattern, flags=flags)
    return pattern.match(doc, action=action, pos=pos, endpos=endpos, action_is_readonly=action_is_readonly)


def search(pattern: MarkdownPatternLike,
           doc: MarkdownDocument,
           action: Callable[[Optional[DocumentElementContentTextMatch]], T] = lambda m: m,
           pos: Optional[int] = None,
           endpos: Optional[int] = None,
           action_is_readonly: bool = True,
           flags: Optional[re.RegexFlag] = None,
           ) -> T:
    """
    Scan through the string of the MarkdownDocument's plaintext looking for a match, and return a match object, or None if no match was found.
    :param pattern: The regular expression pattern to use. If this is a MarkdownDocumentTextPattern, it will be used as-is. Otherwise, it will be compiled into a MarkdownDocumentTextPattern.
    :param doc: The MarkdownDocument to match against.
    :param action: A function to apply to the match object, if one is found. The function should take a single argument, which will be the match object, and return a value of type T.
    :param pos: The position at which to start matching; defaults to the beginning of the string.
    :param endpos: The position at which to end matching; defaults to the end of the string.
    :param action_is_readonly: Whether the document should be treated as read-only while action is running.
    :param flags: A bitwise OR of the flags.
    """

    pattern = compile(pattern, flags=flags)
    return pattern.search(doc, action=action, pos=pos, endpos=endpos, action_is_readonly=action_is_readonly)


def fullmatch(pattern: MarkdownPatternLike,
              doc: MarkdownDocument,
              action: Callable[[Optional[DocumentElementContentTextMatch]], T] = lambda m: m,
              pos: Optional[int] = None,
              endpos: Optional[int] = None,
              action_is_readonly: bool = True,
              flags: Optional[re.RegexFlag] = None,
              ) -> T:
    """
    Try to apply the pattern to the string of the MarkdownDocument's plaintext, returning a match object, or None if no match was found.
    :param pattern: The regular expression pattern to use. If this is a MarkdownDocumentTextPattern, it will be used as-is. Otherwise, it will be compiled into a MarkdownDocumentTextPattern.
    :param doc: The MarkdownDocument to match against.
    :param action: A function to apply to the match object, if one is found. The function should take a single argument, which will be the match object, and return a value of type T.
    :param pos: The position at which to start matching; defaults to the beginning of the string.
    :param endpos: The position at which to end matching; defaults to the end of the string.
    :param action_is_readonly: Whether the document should be treated as read-only while action is running.
    :param flags: A bitwise OR of the flags.
    """

    pattern = compile(pattern, flags=flags)
    return pattern.fullmatch(doc, action=action, pos=pos, endpos=endpos, action_is_readonly=action_is_readonly)


def findall(pattern: MarkdownPatternLike,
            doc: MarkdownDocument,
            action: Callable[[List[Any]], T] = lambda m: m,
            pos: Optional[int] = None,
            endpos: Optional[int] = None,
            flags: Optional[re.RegexFlag] = None,
            ) -> T:
    """
    Return a list of all non-overlapping matches in the string of the MarkdownDocument's plaintext.
    :param pattern: The regular expression pattern to use. If this is a MarkdownDocumentTextPattern, it will be used as-is. Otherwise, it will be compiled into a MarkdownDocumentTextPattern.
    :param doc: The MarkdownDocument to match against.
    :param action: A function to apply to the match object, if one is found. The function should take a single argument, which will be the match object, and return a value of type T.
    :param pos: The position at which to start matching; defaults to the beginning of the string.
    :param endpos: The position at which to end matching; defaults to the end of the string.
    :param flags: A bitwise OR of the flags.
    :return: A value of type T, as determined by the action function.
    """

    pattern = compile(pattern, flags=flags)
    return pattern.findall(doc, action=action, pos=pos, endpos=endpos)


def finditer(pattern: MarkdownPatternLike,
             doc: MarkdownDocument,
             action: Callable[[Iterable[DocumentElementContentTextMatch]], T] = lambda m: m,
             pos: Optional[int] = None,
             endpos: Optional[int] = None,
             action_is_readonly: bool = True,
             flags: Optional[re.RegexFlag] = None,
             ) -> T:
    """
    Return an iterator over all non-overlapping matches in the string of the MarkdownDocument's plaintext.
    :param pattern: The regular expression pattern to use. If this is a MarkdownDocumentTextPattern, it will be used as-is. Otherwise, it will be compiled into a MarkdownDocumentTextPattern.
    :param doc: The MarkdownDocument to match against.
    :param action: A function to apply to the match object, if one is found. The function should take a single argument, which will be the match object, and return a value of type T.
    :param pos: The position at which to start matching; defaults to the beginning of the string.
    :param endpos: The position at which to end matching; defaults to the end of the string.
    :param action_is_readonly: Whether the document should be treated as read-only while action is running.
    :param flags: A bitwise OR of the flags.
    :return: A value of type T, as determined by the action function.
    """

    pattern = compile(pattern, flags=flags)
    return pattern.finditer(doc, action=action, pos=pos, endpos=endpos, action_is_readonly=action_is_readonly)


def sub(pattern: MarkdownPatternLike,
        doc: MarkdownDocument,
        repl: Union[PanfluteElementLike, Callable[[DocumentElementContentTextMatch], PanfluteElementLike]],
        pos: Optional[int] = None,
        endpos: Optional[int] = None,
        flags: Optional[re.RegexFlag] = None,
        ) -> None:
    """
    Update the MarkdownDocument's plaintext to reflect the string obtained by replacing the leftmost non-overlapping
    occurrences of pattern in the MarkdownDocument's plaintext by the replacement repl.
    :param pattern: The regular expression pattern to use. If this is a MarkdownDocumentTextPattern, it will be used as-is. Otherwise, it will be compiled into a MarkdownDocumentTextPattern.
    :param doc: The MarkdownDocument to match against.
    :param repl: The replacement string.
    :param pos: The position at which to start matching; defaults to the beginning of the string.
    :param endpos: The position at which to end matching; defaults to the end of the string.
    :param flags: A bitwise OR of the flags.
    """

    pattern = compile(pattern, flags=flags)
    return pattern.sub(doc, repl, pos=pos, endpos=endpos)[0]


def rm(pattern: MarkdownPatternLike,
       doc: MarkdownDocument,
       pos: Optional[int] = None,
       endpos: Optional[int] = None,
       flags: Optional[re.RegexFlag] = None,
       ) -> None:
    """
    Update the MarkdownDocument's plaintext to reflect the string obtained by removing the leftmost non-overlapping
    occurrences of pattern in the MarkdownDocument's plaintext.
    :param pattern: The regular expression pattern to use. If this is a MarkdownDocumentTextPattern, it will be used as-is. Otherwise, it will be compiled into a MarkdownDocumentTextPattern.
    :param doc: The MarkdownDocument to match against.
    :param pos: The position at which to start matching; defaults to the beginning of the string.
    :param endpos: The position at which to end matching; defaults to the end of the string.
    :param flags: A bitwise OR of the flags.
    """

    pattern = compile(pattern, flags=flags)
    return pattern.rm(doc, pos=pos, endpos=endpos)
