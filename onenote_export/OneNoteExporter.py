from typing import Callable, Dict, Optional, Tuple
import logging
import pathlib

from onenote import \
    OneNoteApplication,\
    OneNoteNode,\
    OneNoteUnfiledNotes,\
    OneNoteOpenSections,\
    OneNoteNotebook,\
    OneNotePage,\
    OneNoteSectionGroup,\
    OneNoteSection
from .OneNoteExportTaskContextFactory import OneNoteExportTaskContextFactory
from .OneNoteExportTaskBase import OneNoteExportTaskBase
from .OneNoteExportTaskFactory import OneNoteExportTaskFactory
from .Pathlike import Pathlike


class OneNoteExporter:
    def __init__(self,
                 task_factory: OneNoteExportTaskFactory,
                 *,
                 logger: logging.Logger = logging.getLogger(__name__),
                 ):
        self._task_factory = task_factory
        self._logger = logger

    def _scan_and_create_export_tasks(self, application: OneNoteApplication) -> Tuple[OneNoteExportTaskBase, ...]:
        export_tasks: Dict[OneNoteNode, OneNoteExportTaskBase] = {}

        def create_export_task(node: OneNoteNode) -> Optional[OneNoteExportTaskBase]:
            if hasattr(node, 'parent'):
                prereqs = (get_or_create_export_task(node.parent),)
            else:
                prereqs = ()
            prereqs = (t for t in prereqs if t is not None)
            return self._task_factory.create_default_for_node_type(node, prereqs)

        def get_or_create_export_task(node: OneNoteNode) -> Optional[OneNoteExportTaskBase]:
            if node not in export_tasks:
                new_task = create_export_task(node)
                export_tasks[node] = new_task
                return new_task
            return export_tasks[node]

        node_stack = (application,)


        self._logger.info('🔍 Scanning OneNote tree…')
        node_count = 0
        while len(node_stack) > 0:
            node = node_stack[0]
            node_stack = node_stack[1:]
            node_count += 1

            get_or_create_export_task(node)
            if isinstance(node, OneNoteApplication):
                self._logger.info('🪟 Found OneNote Application.')
            elif isinstance(node, OneNoteUnfiledNotes):
                self._logger.info('📰 Found Unfiled Notes.')
            elif isinstance(node, OneNoteOpenSections):
                self._logger.info('🗃️ Found Open Sections.')
            elif isinstance(node, OneNoteNotebook):
                self._logger.info(f'📔 Found Notebook "{node.name}".')
            elif isinstance(node, OneNoteSectionGroup):
                self._logger.info(f'🗃️ Found Section Group "{node.name}".')
            elif isinstance(node, OneNoteSection):
                self._logger.info(f'📂 Found Section "{node.name}".')
            elif isinstance(node, OneNotePage):
                self._logger.info(f'📄 Found Page "{node.name}".')
            else:
                raise ValueError(f'Unexpected node type: {type(node)}')

            if hasattr(node, 'children'):
                node_stack = node_stack + tuple(node.children)

        export_tasks_values = tuple(t for t in export_tasks.values() if t is not None)
        self._logger.info(f'📝 Found {node_count} nodes and created {len(export_tasks_values)} export tasks.')
        return export_tasks_values

    def execute_export(self, application: OneNoteApplication) -> None:
        export_tasks = self._scan_and_create_export_tasks(application)

        self._logger.info('🚀 Starting export…')
        for export_task in export_tasks:
            export_task()
        self._logger.info('🏁 Export complete.')


def create_default_onenote_exporter(
    root_output_dir: Pathlike,
    page_relative_assets_dir: Pathlike,
    path_component_scrubber: Callable[[str], pathlib.Path],
    should_export: Callable[[OneNoteNode], bool] = lambda node: True
) -> 'OneNoteExporter':
    context_factory = OneNoteExportTaskContextFactory(
        root_output_dir=root_output_dir,
        page_relative_assets_dir=page_relative_assets_dir,
        path_component_scrubber=path_component_scrubber,
    )

    return OneNoteExporter(
        task_factory=OneNoteExportTaskFactory(context_factory=context_factory, should_export=should_export),
    )
