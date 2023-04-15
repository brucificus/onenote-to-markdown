import os
from typing import Optional

import panflute


def commit_element_suicide(e: panflute.Element) -> Optional[panflute.Element]:
    parent = e.parent
    if parent is not None:
        parent.content.remove(e)
    return parent


def read_content_text_from_Space(e: panflute.Space) -> str:
    return ' '


def len_content_text_from_Space(e: panflute.Space) -> int:
    return len(' ')


def read_content_text_from_SoftBreak(e: panflute.SoftBreak) -> str:
    return ' '


def len_content_text_from_SoftBreak(e: panflute.SoftBreak) -> int:
    return len(' ')


def read_content_text_from_LineBreak(e: panflute.LineBreak) -> str:
    return os.linesep


def len_content_text_from_LineBreak(e: panflute.LineBreak) -> int:
    return len(os.linesep)


def read_content_text_from_Link(e: panflute.Link) -> str:
    return e.title


def len_content_text_from_Link(e: panflute.Link) -> int:
    return len(e.title)


def set_content_text_to_Link(e: panflute.Link, new_text: str) -> None:
    e.title = new_text


def read_content_text_from_Image(e: panflute.Image) -> str:
    return e.title


def len_content_text_from_Image(e: panflute.Image) -> int:
    return len(e.title)


def set_content_text_to_Image(e: panflute.Image, new_text: str) -> None:
    e.title = new_text


def read_content_text_from_Str(e: panflute.Str) -> str:
    return e.text


def len_content_text_from_Str(e: panflute.Str) -> int:
    return len(e.text)


def set_content_text_to_Str(e: panflute.Str, new_text: str) -> None:
    e.text = new_text


def read_content_text_from_RawBlock(e: panflute.RawBlock) -> str:
    raise NotImplementedError()


def len_content_text_from_RawBlock(e: panflute.RawBlock) -> int:
    raise NotImplementedError()


def set_content_text_to_RawBlock(e: panflute.RawBlock, new_text: str) -> None:
    raise NotImplementedError()


def read_content_text_from_Code(e: panflute.Code) -> str:
    raise NotImplementedError()


def len_content_text_from_Code(e: panflute.Code) -> int:
    raise NotImplementedError()


def set_content_text_to_Code(e: panflute.Code, new_text: str) -> None:
    raise NotImplementedError()


def read_content_text_from_Math(e: panflute.Math) -> str:
    raise NotImplementedError()


def len_content_text_from_Math(e: panflute.Math) -> int:
    raise NotImplementedError()


def set_content_text_to_Math(e: panflute.Math, new_text: str) -> None:
    raise NotImplementedError()


def read_content_text_from_RawInline(e: panflute.RawInline) -> str:
    raise NotImplementedError()


def len_content_text_from_RawInline(e: panflute.RawInline) -> int:
    raise NotImplementedError()


def set_content_text_to_RawInline(e: panflute.RawInline, new_text: str) -> None:
    raise NotImplementedError()


def read_content_text_from_MetaString(e: panflute.MetaString) -> str:
    return e.text


def len_content_text_from_MetaString(e: panflute.MetaString) -> int:
    return len(e.text)


def set_content_text_to_MetaString(e: panflute.MetaString, new_text: str) -> None:
    e.text = new_text
