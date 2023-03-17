from typing import Callable

from .OneNoteExportMiddlewareContext import OneNoteExportMiddlewareContext
from .OneNoteExportMiddlewarePartial import OneNoteExportMiddlewarePartial
from .type_variables import TNode, TReturn


OneNoteExportMiddleware =\
    Callable[[OneNoteExportMiddlewareContext[TNode], OneNoteExportMiddlewarePartial], TReturn]
