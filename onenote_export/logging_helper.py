import logging
from functools import lru_cache
from typing import Optional

from onenote import OneNoteNode, OneNoteApplication, OneNoteNotebook, OneNoteSectionGroup, OneNotePage, OneNoteSection, \
    OneNoteUnfiledNotes, OneNoteOpenSections


def _get_logger_name_part(onenote_node: OneNoteNode) -> Optional[str]:
    if onenote_node is None:
        return None
    if isinstance(onenote_node, OneNoteApplication):
        return "OneNote"

    if isinstance(onenote_node, OneNoteNotebook):
        return f'Notebook[{onenote_node.index}]'

    if isinstance(onenote_node, OneNoteSectionGroup):
        return f'SectionGroup[{onenote_node.index}]'

    if isinstance(onenote_node, OneNoteOpenSections):
        return f'OpenSections[{onenote_node.index}]'

    if isinstance(onenote_node, OneNoteUnfiledNotes):
        return f'UnfiledNotes[{onenote_node.index}]'

    if isinstance(onenote_node, OneNoteSection):
        return f'Section[{onenote_node.index}]'

    if isinstance(onenote_node, OneNotePage):
        return f'Page[{onenote_node.index}]'

    raise TypeError(f'Unexpected type: {type(onenote_node)}')


def _get_onenote_node_logger(onenote_node: OneNoteNode) -> logging.Logger:
    if hasattr(onenote_node, 'parent') and onenote_node.parent is not None:
        parent_logger = _get_onenote_node_logger(onenote_node.parent)
    else:
        parent_logger = logging.root

    child_logger_name_part = _get_logger_name_part(onenote_node)

    if child_logger_name_part is None:
        return parent_logger

    return parent_logger.getChild(child_logger_name_part)


def _create_console_logger_handler_for_exact_level(level: int, symbol: str) -> logging.Handler:
    # Customize format for each log level
    formatter = logging.Formatter(
        fmt=f'%(asctime)s {symbol}%(levelname)-8s %(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    console_handler.addFilter(lambda record: record.levelno == level)
    return console_handler


@lru_cache(maxsize=128)
def get_logger(*, module_name: str, onenote_node: OneNoteNode) -> logging.Logger:
    parent_logger = _get_onenote_node_logger(onenote_node)

    if module_name is None:
        result_logger = parent_logger
    else:
        result_logger = parent_logger.getChild(module_name)

    if not result_logger.handlers:
        result_logger.addHandler(_create_console_logger_handler_for_exact_level(logging.DEBUG, '📜'))
        result_logger.addHandler(_create_console_logger_handler_for_exact_level(logging.INFO, 'ℹ️'))
        result_logger.addHandler(_create_console_logger_handler_for_exact_level(logging.WARNING, '⚠️'))
        result_logger.addHandler(_create_console_logger_handler_for_exact_level(logging.ERROR, '❗'))
        result_logger.addHandler(_create_console_logger_handler_for_exact_level(logging.CRITICAL, '🛑'))
        result_logger.propagate = False

    return result_logger
