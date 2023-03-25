import logging
import pathlib
from typing import Generic, Optional

from .Pathlike import Pathlike
from .type_variables import TNode
from .logging_helper import get_logger


class OneNoteExportTaskContext(Generic[TNode]):
    def __init__(self,
                 node: TNode,
                 output_dir: Pathlike,
                 assets_dir: Pathlike,
                 safe_filename_base: Optional[pathlib.Path],
                 ):
        self._node = node
        self._output_dir = output_dir
        self._assets_dir = assets_dir
        self._safe_filename_base = safe_filename_base

    @property
    def node(self) -> TNode: return self._node

    @property
    def output_dir(self) -> Pathlike: return self._output_dir

    @property
    def assets_dir(self) -> str: return self._assets_dir

    @property
    def safe_filename_base(self) -> Optional[pathlib.Path]: return self._safe_filename_base

    def get_logger(self, module_name: str) -> logging.Logger:
        return get_logger(module_name=module_name, onenote_node=self.node)
