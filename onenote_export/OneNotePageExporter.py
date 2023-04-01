from typing import Iterable, Tuple

import onenote_export.page_ensure_assets_dir_exists
import onenote_export.page_ensure_output_dir_exists
import onenote_export.page_export_pandoc_ast_to_markdown_file
import onenote_export.page_pdf_patch_images_into_md
import onenote_export.page_reparse_embedded_html

from .OneNoteExportTaskBase import OneNoteExportTaskBase
from .OneNoteExportTaskFactory import OneNoteExportTaskFactory
from .OneNotePageExportTaskContext import OneNotePageExportTaskContext


class OneNotePageExporter(OneNoteExportTaskBase):
    def __init__(self,
                 context: OneNotePageExportTaskContext,
                 prerequisites: Iterable[OneNoteExportTaskBase],
                 subtask_factory: OneNoteExportTaskFactory,
                 ):
        super().__init__(prerequisites)
        if not isinstance(context, OneNotePageExportTaskContext):
            raise TypeError(f"Context must be an instance of OneNotePageExportMiddlewareContext, not {type(context)}")
        self._context = context
        self._subtasks = tuple(OneNotePageExporter._yield_subtasks(context, tuple(), subtask_factory))

    @staticmethod
    def _yield_subtasks(context: OneNotePageExportTaskContext, prerequisites: Tuple[OneNoteExportTaskBase], subtask_factory: OneNoteExportTaskFactory) -> Iterable['OneNoteExportTask']:
        create_subtask = subtask_factory.create_from_spec

        task_ensure_output_dir_exists = create_subtask(context.node, task_spec=onenote_export.page_ensure_output_dir_exists.page_ensure_output_dir_exists, prerequisites=prerequisites)
        yield task_ensure_output_dir_exists

        task_ensure_assets_dir_exists = create_subtask(context.node, task_spec=onenote_export.page_ensure_assets_dir_exists.page_ensure_assets_dir_exists, prerequisites=prerequisites + (task_ensure_output_dir_exists,))
        yield task_ensure_assets_dir_exists

        task_page_reparse_embedded_html = create_subtask(context.node, task_spec=onenote_export.page_reparse_embedded_html.page_reparse_embedded_html, prerequisites=prerequisites)
        yield task_page_reparse_embedded_html

        task_pdf_patch_images_into_md = create_subtask(context.node, task_spec=onenote_export.page_pdf_patch_images_into_md.page_pdf_patch_images_into_md, prerequisites=(task_ensure_assets_dir_exists, task_page_reparse_embedded_html,))
        yield task_pdf_patch_images_into_md

        task_export_pandoc_ast_to_markdown_file = create_subtask(context.node, task_spec=onenote_export.page_export_pandoc_ast_to_markdown_file.page_export_pandoc_ast_to_markdown_file, prerequisites=(task_pdf_patch_images_into_md,))
        yield task_export_pandoc_ast_to_markdown_file

    def _execute(self):
        with self._context:
            for subtask in self._subtasks:
                subtask()


OneNoteExportTaskBase.register(OneNotePageExporter)
