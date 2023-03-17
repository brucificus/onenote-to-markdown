from typing import Callable

from .OneNoteExportMiddlewareContext import OneNoteExportMiddlewareContext
from .type_variables import TNode, TReturn


OneNoteExportMiddlewarePartial =\
    Callable[[OneNoteExportMiddlewareContext[TNode]], TReturn]
