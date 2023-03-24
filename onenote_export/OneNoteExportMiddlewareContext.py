import logging
from typing import Generic, Callable

from .Pathlike import Pathlike
from .type_variables import TNode
from .logging_helper import get_logger


class OneNoteExportMiddlewareContext(Generic[TNode]):
    def __init__(self,
                 node: TNode,
                 output_dir: Pathlike,
                 assets_dir: Pathlike,
                 convert_node_name_to_path_component: Callable[[str], Pathlike]
                 ):
        self._node = node
        self._output_dir = output_dir
        self._assets_dir = assets_dir
        self._convert_node_name_to_path_component = convert_node_name_to_path_component

    @property
    def node(self) -> TNode: return self._node

    @property
    def output_dir(self) -> Pathlike: return self._output_dir

    @property
    def assets_dir(self) -> str: return self._assets_dir

    @property
    def convert_node_name_to_path_component(self) -> Callable[[str], Pathlike]:
        return self._convert_node_name_to_path_component

    def get_logger(self, module_name: str) -> logging.Logger:
        return get_logger(module_name=module_name, onenote_node=self.node)
