import logging

import pywintypes
from typing import Iterable, Tuple, Callable

from .OneNoteExportTaskBase import OneNoteExportTaskBase
from .OneNoteExportTaskFactory import OneNoteExportTaskFactory
from .OneNotePageExportTaskContext import OneNotePageExportTaskContext
from .page_export_tasks import *


class OneNotePageExporter(OneNoteExportTaskBase):
    def __init__(self,
                 context: OneNotePageExportTaskContext,
                 prerequisites: Iterable[OneNoteExportTaskBase],
                 subtask_factory: OneNoteExportTaskFactory,
                 *,
                 logger: logging.Logger = logging.getLogger(__name__ + '.' + __qualname__),
                 ):
        super().__init__(prerequisites)
        if not isinstance(context, OneNotePageExportTaskContext):
            raise TypeError(f"Context must be an instance of OneNotePageExportMiddlewareContext, not {type(context)}")
        self._context = context
        self._subtasks = tuple(OneNotePageExporter._yield_subtasks(context, tuple(), subtask_factory))
        self._logger = logger

    @staticmethod
    def _yield_subtasks(
        context: OneNotePageExportTaskContext,
        prerequisites: Tuple[OneNoteExportTaskBase],
        subtask_factory: OneNoteExportTaskFactory
    ) -> Iterable['OneNoteExportTask']:
        create_subtask = subtask_factory.create_from_spec

        task_ensure_output_dir_exists = create_subtask(
            context.node,
            task_spec=page_ensure_output_dir_exists,
            prerequisites=prerequisites
        )
        yield task_ensure_output_dir_exists

        task_ensure_assets_dir_exists = create_subtask(
            context.node,
            task_spec=page_ensure_assets_dir_exists,
            prerequisites=prerequisites + (task_ensure_output_dir_exists,)
        )
        yield task_ensure_assets_dir_exists

        task_page_reparse_embedded_html = create_subtask(
            context.node,
            task_spec=page_reparse_embedded_html,
            prerequisites=prerequisites
        )
        yield task_page_reparse_embedded_html

        task_pdf_patch_images_into_md = create_subtask(
            context.node,
            task_spec=page_pdf_patch_images_into_md,
            prerequisites=(task_ensure_assets_dir_exists, task_page_reparse_embedded_html,)
        )
        yield task_pdf_patch_images_into_md

        task_export_pandoc_ast_to_markdown_file = create_subtask(
            context.node,
            task_spec=page_export_pandoc_ast_to_markdown_file,
            prerequisites=(task_pdf_patch_images_into_md,)
        )
        yield task_export_pandoc_ast_to_markdown_file


    def _execute(self):
        had_com_failure = None

        def handle_com_failure(e: Exception, activity_description: str) -> bool:
            def exception_is_or_has_cause(e: Exception, predicate: Callable[[Exception], bool]) -> bool:
                if isinstance(e, BaseException):
                    if predicate(e):
                        return True
                    if e.__cause__ and predicate(e.__cause__):
                        return True
                    if e.args and any(exception_is_or_has_cause(arg, predicate) for arg in e.args):
                        return True
                return False

            is_com_failure = exception_is_or_has_cause(e, lambda e: isinstance(e, pywintypes.com_error))
            if is_com_failure:
                self._logger.error(f"Unrecoverable COM error while {activity_description}.", exc_info=e)
            return is_com_failure

        try:
            with self._context:
                for subtask in self._subtasks:
                    try:
                        subtask()
                    except Exception as e:
                        had_com_failure = handle_com_failure(e, f"executing subtask {subtask}")
                        if had_com_failure:
                            break
                        else:
                            raise
        except Exception as e:
            had_com_failure = had_com_failure or handle_com_failure(e, f"preparing to execute subtasks")
            if had_com_failure:
                return
            else:
                raise


OneNoteExportTaskBase.register(OneNotePageExporter)
