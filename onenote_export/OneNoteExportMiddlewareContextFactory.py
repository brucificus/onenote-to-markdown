import pathlib
from typing import Callable

from onenote import OneNoteNode, OneNotePage, OneNoteApplication
from .OneNoteExportMiddlewareContext import OneNoteExportMiddlewareContext
from .OneNotePageExportMiddlewareContext import OneNotePageExportMiddlewareContext
from .Pathlike import Pathlike


class OneNoteExportMiddlewareContextFactory:
    def __init__(self,
                 root_output_dir: Pathlike,
                 page_relative_assets_dir: Pathlike,
                 convert_node_name_to_path_component: Callable[[str], pathlib.Path],
                 ):
        self._root_output_dir =\
            pathlib.Path(root_output_dir) if isinstance(root_output_dir, str) else root_output_dir
        self._page_relative_assets_dir =\
            pathlib.Path(page_relative_assets_dir) if isinstance(page_relative_assets_dir, str) else page_relative_assets_dir
        self._convert_node_name_to_path_component = convert_node_name_to_path_component

    @staticmethod
    def _is_output_dir_step_down(current_context: OneNoteExportMiddlewareContext[OneNoteNode], child: OneNoteNode) -> bool:
        if not isinstance(child, OneNotePage) and not isinstance(current_context.node, OneNotePage):
            return True
        return False

    def create_context_for_traversal_transition_to_child(self, current_context: OneNoteExportMiddlewareContext[OneNoteNode], child: OneNoteNode) -> OneNoteExportMiddlewareContext[OneNoteNode]:
        convert_node_name_to_path_component = current_context.convert_node_name_to_path_component

        if not current_context.output_dir or len(current_context.output_dir.parts) == 0:
            new_output_dir = self._root_output_dir
            new_assets_dir = self._page_relative_assets_dir
        elif OneNoteExportMiddlewareContextFactory._is_output_dir_step_down(current_context, child):
            child_name = child.name
            if not child_name:
                raise ValueError(f'Cannot create context for child node {child} of because child node does not have a name')
            new_output_dir = current_context.output_dir / convert_node_name_to_path_component(child_name)
            new_assets_dir = self._page_relative_assets_dir
        else:
            new_output_dir = current_context.output_dir
            new_assets_dir = current_context.assets_dir

        context = OneNoteExportMiddlewareContext(
            node=child,
            output_dir=new_output_dir,
            assets_dir=new_assets_dir,
            convert_node_name_to_path_component=self._convert_node_name_to_path_component
        )

        if isinstance(child, OneNotePage):
            context = OneNotePageExportMiddlewareContext.begin_export(context)

        return context


    def create_context_for_application(self, node: OneNoteApplication) -> OneNoteExportMiddlewareContext[OneNoteApplication]:
        current_output_dir = self._root_output_dir
        return OneNoteExportMiddlewareContext(
            node=node,
            output_dir=current_output_dir,
            assets_dir=current_output_dir / self._page_relative_assets_dir,
            convert_node_name_to_path_component=self._convert_node_name_to_path_component
        )
