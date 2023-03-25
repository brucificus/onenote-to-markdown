import pathlib
from typing import Callable

from onenote import OneNoteNode, OneNotePage, OneNoteApplication
from .OneNoteExportTaskContext import OneNoteExportTaskContext
from .OneNotePageExportTaskContext import OneNotePageExportTaskContext
from .Pathlike import Pathlike


class OneNoteExportTaskContextFactory:
    def __init__(self,
                 root_output_dir: Pathlike,
                 page_relative_assets_dir: Pathlike,
                 path_component_scrubber: Callable[[str], pathlib.Path],
                 ):
        self._root_output_dir =\
            pathlib.Path(root_output_dir) if isinstance(root_output_dir, str) else root_output_dir
        self._page_relative_assets_dir =\
            pathlib.Path(page_relative_assets_dir) if isinstance(page_relative_assets_dir, str) else page_relative_assets_dir
        self._path_component_scrubber = path_component_scrubber

    @staticmethod
    def _is_output_dir_step_down(current_context: OneNoteExportTaskContext[OneNoteNode], child: OneNoteNode) -> bool:
        return not isinstance(child, OneNotePage) and not isinstance(current_context.node, OneNotePage)

    def create_context_for_traversal_transition_to_child(self, parent_context: OneNoteExportTaskContext[OneNoteNode], child: OneNoteNode) -> OneNoteExportTaskContext[OneNoteNode]:
        child_safe_filename_base = self._path_component_scrubber(child.name)
        if not parent_context.output_dir or len(parent_context.output_dir.parts) == 0:
            new_output_dir = self._root_output_dir
        elif OneNoteExportTaskContextFactory._is_output_dir_step_down(parent_context, child):
            new_output_dir = parent_context.output_dir / child_safe_filename_base
        else:
            new_output_dir = parent_context.output_dir

        child_context = OneNoteExportTaskContext(
            node=child,
            output_dir=new_output_dir,
            assets_dir=self._page_relative_assets_dir,
            safe_filename_base=child_safe_filename_base,
        )

        if isinstance(child, OneNotePage):
            child_context = OneNotePageExportTaskContext.begin_export(child_context)

        return child_context

    def create_context_for_application(self, node: OneNoteApplication) -> OneNoteExportTaskContext[OneNoteApplication]:
        current_output_dir = self._root_output_dir
        return OneNoteExportTaskContext(
            node=node,
            output_dir=current_output_dir,
            assets_dir=current_output_dir / self._page_relative_assets_dir,
            safe_filename_base=None,
        )
