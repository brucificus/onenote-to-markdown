import functools
import pathlib
from functools import cache
from typing import ContextManager, Callable

import pypandoc

from markdown_dom.MarkdownDocument import MarkdownDocument
from onenote import OneNotePage
from onenote_export.OneNoteExportTaskContext import OneNoteExportTaskContext
from onenote_export.OneNotePageDocxExportError import OneNotePageDocxExportError
from onenote_export.OneNotePagePdfExportError import OneNotePagePdfExportError
from onenote_export.TemporaryOneNotePageDocxExport import TemporaryOneNotePageDocxExport
from onenote_export.TemporaryOneNotePagePdfExport import TemporaryOneNotePagePdfExport
from pdf_inspection.PdfDocument import PdfDocument



default_create_temporary_pdf_export_handler = TemporaryOneNotePagePdfExport
default_create_temporary_docx_export_handler = TemporaryOneNotePageDocxExport


def default_create_output_md_document(context: 'OneNotePageExportTaskContext') -> MarkdownDocument:
    md_path = context.output_md_path
    if not context._temp_docx_export:
        raise RuntimeError(
            "OneNotePageExportTaskContext must be entered before calling accessing the output markdown document")

    if md_path.exists():
        def get_replacement_ast():
            with context._temp_docx_export:
                return context.page_as_docx_pandoc_ast_json
        doc = MarkdownDocument.import_md_file(md_path)
        doc._replace_pandoc_ast_json(get_replacement_ast())
    else:
        def get_initial_ast():
            with context._temp_docx_export:
                return context.page_as_docx_pandoc_ast_json
        doc = MarkdownDocument.open_document_ast_json_str(
            initial_document_ast_json=get_initial_ast,
            output_md_path=md_path,
        )
    return doc


class OneNotePageExportTaskContext(OneNoteExportTaskContext[OneNotePage], ContextManager):
    def __init__(self,
                 context: OneNoteExportTaskContext[OneNotePage],
                 *,
                 create_temporary_pdf_export_handler: Callable[[OneNotePage], TemporaryOneNotePagePdfExport] = TemporaryOneNotePagePdfExport,
                 create_temporary_docx_export_handler: Callable[[OneNotePage], TemporaryOneNotePageDocxExport] = TemporaryOneNotePageDocxExport,
                 create_output_md_document: Callable[['OneNotePageExportTaskContext'], MarkdownDocument] = default_create_output_md_document,
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
        self._create_output_md_document = functools.partial(create_output_md_document, self)
        self._temp_pdf_export: TemporaryOneNotePagePdfExport = None
        self._temp_docx_export: TemporaryOneNotePageDocxExport = None
        self._temp_docx_export_pandoc_ast_json: str = None
        self._output_md_document: MarkdownDocument = None

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
        self._output_md_document = self._create_output_md_document()

        try:
            self._temp_pdf_export.__enter__()
        except Exception as e:
            raise OneNotePagePdfExportError(self._page, e) from e

        try:
            self._temp_docx_export.__enter__()
        except Exception as e:
            raise OneNotePageDocxExportError(self._page, e) from e

        return self

    @property
    @cache
    def page_as_pdf_document(self) -> PdfDocument:
        if self._temp_pdf_export is None:
            raise RuntimeError("OneNotePageExportTaskContext must be entered before accessing page_as_pdf_document")
        return self._temp_pdf_export.pdf_document

    @property
    def page_as_docx_pandoc_ast_json(self) -> str:
        if self._temp_docx_export is None:
            raise RuntimeError("OneNotePageExportTaskContext must be entered before accessing page_as_docx_pandoc_ast_json")
        if self._temp_docx_export_pandoc_ast_json is None:
            self._temp_docx_export_pandoc_ast_json = self._temp_docx_export.create_pandoc_ast_json()
        return self._temp_docx_export_pandoc_ast_json

    @property
    def output_md_document(self) -> MarkdownDocument:
        if self._output_md_document is None:
            raise RuntimeError("OneNotePageExportTaskContext must be entered before accessing output_md_document")
        return self._output_md_document

    @property
    def pandoc_path(self) -> pathlib.Path:
        return pathlib.Path(pypandoc.get_pandoc_path())

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._temp_pdf_export:
            self._temp_pdf_export.__exit__(exc_type, exc_val, exc_tb)
            self._temp_pdf_export = None
        if self._temp_docx_export:
            self._temp_docx_export.__exit__(exc_type, exc_val, exc_tb)
            self._temp_docx_export = None
        self._temp_docx_export_pandoc_ast_json = None
