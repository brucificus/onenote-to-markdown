import functools
import logging

import pywintypes
from typing import Iterable, Tuple, Callable

from .OneNoteExportTaskBase import OneNoteExportTaskBase
from .OneNoteExportTaskFactory import OneNoteExportTaskFactory
from .OneNotePageExportTaskContext import OneNotePageExportTaskContext
from .OneNotePageExporterSettings import OneNotePageExporterSettings
from .page_export_tasks import *
from .page_export_tasks.page_remove_extraneous_element_attributes import page_remove_extraneous_element_attributes
from .page_export_tasks.page_remove_onenote_footer import page_remove_onenote_footer
from .page_export_tasks.page_remove_redundant_vestigial_stylings import page_remove_redundant_vestigial_stylings


class OneNotePageExporter(OneNoteExportTaskBase):
    def __init__(self,
                 context: OneNotePageExportTaskContext,
                 prerequisites: Iterable[OneNoteExportTaskBase],
                 subtask_factory: OneNoteExportTaskFactory,
                 settings: OneNotePageExporterSettings,
                 *,
                 logger: logging.Logger = logging.getLogger(__name__ + '.' + __qualname__),
                 ):
        super().__init__(prerequisites)
        if not isinstance(context, OneNotePageExportTaskContext):
            raise TypeError(f"Context must be an instance of OneNotePageExportMiddlewareContext, not {type(context)}")
        self._context = context
        self._settings = settings
        self._logger = logger
        self._subtasks = tuple(self._yield_subtasks(context, tuple(), subtask_factory))

    def _yield_subtasks(
        self,
        context: OneNotePageExportTaskContext,
        prerequisites: Tuple[OneNoteExportTaskBase],
        subtask_factory: OneNoteExportTaskFactory
    ) -> Iterable['OneNoteExportTask']:
        create_subtask = functools.partial(subtask_factory.create_from_spec, node=context.node)

        task_ensure_output_dir_exists = create_subtask(
            task_spec=page_ensure_output_dir_exists,
            prerequisites=prerequisites
        )
        yield task_ensure_output_dir_exists

        task_ensure_assets_dir_exists = create_subtask(
            task_spec=page_ensure_assets_dir_exists,
            prerequisites=prerequisites + (task_ensure_output_dir_exists,)
        )
        yield task_ensure_assets_dir_exists

        task_page_reparse_embedded_html = create_subtask(
            task_spec=page_reparse_embedded_html,
            prerequisites=prerequisites
        )
        yield task_page_reparse_embedded_html

        task_page_extract_ordinated_assets_and_relink = create_subtask(
            task_spec=page_extract_ordinated_assets_and_relink,
            prerequisites=(task_ensure_assets_dir_exists, task_page_reparse_embedded_html,)
        )
        yield task_page_extract_ordinated_assets_and_relink

        task_pdf_patch_images_into_md = create_subtask(
            task_spec=page_pdf_patch_images_into_md,
            prerequisites=(task_page_extract_ordinated_assets_and_relink,)
        )
        yield task_pdf_patch_images_into_md

        undepended_tasks = (
            task_page_extract_ordinated_assets_and_relink,
            task_pdf_patch_images_into_md,
        )

        major_document_content_shifts_prereqs = ()

        if self._settings.pages_extra_attributes_settings:
            major_document_content_shifts_prereqs += undepended_tasks
            undepended_tasks = ()
            task_page_remove_extraneous_element_attributes = create_subtask(
                task_spec=page_remove_extraneous_element_attributes,
                prerequisites=major_document_content_shifts_prereqs
            )
            undepended_tasks += (task_page_remove_extraneous_element_attributes,)
            yield task_page_remove_extraneous_element_attributes

        if self._settings.pages_content_class_settings or self._settings.pages_content_style_settings:
            major_document_content_shifts_prereqs += undepended_tasks
            undepended_tasks = ()
            task_page_remove_redundant_vestigial_stylings = create_subtask(
                task_spec=page_remove_redundant_vestigial_stylings,
                prerequisites=major_document_content_shifts_prereqs,
            )
            undepended_tasks += (task_page_remove_redundant_vestigial_stylings,)
            yield task_page_remove_redundant_vestigial_stylings

        text_search_patches_prereqs = ()

        if self._settings.pages_remove_onenote_footer:
            text_search_patches_prereqs += undepended_tasks
            undepended_tasks = ()
            task_page_remove_onenote_footer = create_subtask(
                task_spec=page_remove_onenote_footer,
                prerequisites=text_search_patches_prereqs
            )
            undepended_tasks += (task_page_remove_onenote_footer,)
            yield task_page_remove_onenote_footer

        task_export_pandoc_ast_to_markdown_file = create_subtask(
            task_spec=page_export_pandoc_ast_to_markdown_file,
            prerequisites=undepended_tasks
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
                        raise
        except Exception as e:
            had_com_failure = had_com_failure or handle_com_failure(e, f"preparing to execute subtasks")
            if had_com_failure:
                return
            raise


OneNoteExportTaskBase.register(OneNotePageExporter)
