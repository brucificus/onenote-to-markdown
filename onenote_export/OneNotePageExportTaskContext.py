import functools
import pathlib
from functools import cache
from typing import ContextManager, Callable

from onenote import OneNotePage
from onenote_export.OneNoteExportTaskContext import OneNoteExportTaskContext
from onenote_export.OneNotePageDocxExportError import OneNotePageDocxExportError
from onenote_export.OneNotePagePandocConversionError import OneNotePagePandocConversionError
from onenote_export.OneNotePagePdfExportError import OneNotePagePdfExportError
from onenote_export.TemporaryOneNotePageDocxExport import TemporaryOneNotePageDocxExport
from onenote_export.TemporaryOneNotePagePdfExport import TemporaryOneNotePagePdfExport
from pdf_inspection.PdfDocument import PdfDocument


class OneNotePageExportTaskContext(OneNoteExportTaskContext[OneNotePage], ContextManager):
    def __init__(self,
                 context: OneNoteExportTaskContext[OneNotePage],
                 *,
                 create_temporary_pdf_export_handler: Callable[[OneNotePage], TemporaryOneNotePagePdfExport] = TemporaryOneNotePagePdfExport,
                 create_temporary_docx_export_handler: Callable[[OneNotePage], TemporaryOneNotePageDocxExport] = TemporaryOneNotePageDocxExport,
                 ):
        if not isinstance(context, OneNoteExportTaskContext):
            raise TypeError(f"Context must be an instance of OneNoteExportMiddlewareContext, not {type(context)}")
        page = context.node
        if not isinstance(page, OneNotePage):
            raise TypeError(f"Page must be an instance of OneNotePage, not {type(page)}")
        super().__init__(context.node, context.output_dir, context.assets_dir, context.safe_filename_base)
        self._output_md_path = (context.output_dir / self.safe_filename_base).with_suffix('.md')
        self._output_assets_dir_path = context.output_dir / context.assets_dir
        self._create_temporary_pdf_export_handler = functools.partial(create_temporary_pdf_export_handler, page)
        self._create_temporary_docx_export_handler = functools.partial(create_temporary_docx_export_handler, page)
        self._temp_docx_export: TemporaryOneNotePageDocxExport = None
        self._temp_pdf_export: TemporaryOneNotePagePdfExport = None

    @staticmethod
    def begin_export(context: OneNoteExportTaskContext[OneNotePage]) -> 'OneNotePageExportTaskContext':
        if isinstance(context, OneNotePageExportTaskContext):
            raise TypeError(f"Context must not be an instance of OneNotePageExportMiddlewareContext, not {type(context)}")
        return OneNotePageExportTaskContext(context)

    @property
    def _page(self) -> OneNotePage:
        return self._node

    @property
    @cache
    def page_node_id(self) -> str:
        return self._page.node_id

    @property
    @cache
    def page_name(self) -> str:
        return self._page.name

    @property
    @cache
    def page_route(self) -> tuple[str, ...]:
        return self._page.route

    @property
    def page_index(self) -> int:
        return self._page.index

    @property
    def output_md_path(self) -> pathlib.Path:
        return self._output_md_path

    @property
    def output_assets_dir_path(self) -> pathlib.Path:
        return self._output_assets_dir_path

    def __enter__(self) -> 'OneNotePageExportTaskContext':
        self._temp_pdf_export = self._create_temporary_pdf_export_handler()
        self._temp_docx_export = self._create_temporary_docx_export_handler()

        try:
            self._temp_pdf_export.__enter__()
        except Exception as e:
            raise OneNotePagePdfExportError(self._page, e) from e

        try:
            self._temp_docx_export.__enter__()
        except Exception as e:
            raise OneNotePageDocxExportError(self._page, e) from e

        return self

    def run_pandoc_conversion_to_markdown(self):
        if self._temp_docx_export is None:
            raise RuntimeError("OneNotePageExport must be entered before calling run_pandoc_conversion_to_markdown")
        self._output_md_path.parent.mkdir(parents=True, exist_ok=True)
        self._output_assets_dir_path.mkdir(parents=True, exist_ok=True)
        try:
            return self._temp_docx_export.run_pandoc_conversion_to_markdown(self._output_md_path)
        except Exception as e:
            raise OneNotePagePandocConversionError(self._page, e) from e

    @property
    @cache
    def page_as_pdf_document(self) -> PdfDocument:
        if self._temp_pdf_export is None:
            raise RuntimeError("OneNotePageExport must be entered before accessing page_as_pdf_document")
        return self._temp_pdf_export.pdf_document

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._temp_pdf_export.__exit__(exc_type, exc_val, exc_tb)
        self._temp_docx_export.__exit__(exc_type, exc_val, exc_tb)
        self._temp_pdf_export = None
        self._temp_docx_export = None
