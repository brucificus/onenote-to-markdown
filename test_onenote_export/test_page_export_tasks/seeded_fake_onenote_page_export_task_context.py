import pathlib
import shutil

from typing import Optional
from unittest.mock import MagicMock

from fitz import fitz

from markdown_dom.MarkdownDocument import MarkdownDocument
from mhtml_dom.MhtmlContainer import MhtmlContainer
from onenote.OneNotePage import OneNotePage
from onenote_export.OneNoteExportTaskContext import OneNoteExportTaskContext
from onenote_export.Pathlike import Pathlike
from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext
from onenote_export.TemporaryOneNotePageDocxExport import TemporaryOneNotePageDocxExport
from onenote_export.TemporaryOneNotePageMhtmlExport import TemporaryOneNotePageMhtmlExport
from onenote_export.TemporaryOneNotePagePdfExport import TemporaryOneNotePagePdfExport
from onenote_export.temporary_file import TemporaryFilePath
from pdf_inspection.PdfDocument import PdfDocument


def create_mock_page(
    name: str,
    sample_mhtml_path: Optional[Pathlike] = None,
    sample_docx_path: Optional[Pathlike] = None,
    sample_pdf_path: Optional[Pathlike] = None,
) -> OneNotePage:
    mock_page = MagicMock(spec=OneNotePage)
    mock_page.children = ()
    mock_page.name = name
    mock_page.parent = None
    mock_page.node_id = 'mock_node_id'
    mock_page.index = 0

    def replacement_export_mhtml(path: pathlib.Path):
        if sample_mhtml_path is not None:
            shutil.copyfile(sample_mhtml_path, path)
        else:
            raise NotImplementedError()
    mock_page._export_mhtml = replacement_export_mhtml

    def replacement_export_docx(path: pathlib.Path):
        if sample_docx_path is not None:
            shutil.copyfile(sample_docx_path, path)
        else:
            raise NotImplementedError()
    mock_page._export_docx = replacement_export_docx

    def replacement_export_pdf(path: pathlib.Path):
        if sample_pdf_path is not None:
            shutil.copyfile(sample_pdf_path, path)
    mock_page._export_pdf = replacement_export_pdf

    return mock_page

def create_seeded_fake_onenote_page_export_task_context(
    sample_docx_path: Optional[Pathlike] = None,
    sample_pdf_path: Optional[Pathlike] = None,
    sample_md_path: Optional[Pathlike] = None,
) -> OneNotePageExportTaskContext:
    if not isinstance(sample_docx_path, pathlib.Path) and sample_docx_path is not None:
        sample_docx_path = pathlib.Path(str(sample_docx_path))
    if not isinstance(sample_pdf_path, pathlib.Path) and sample_pdf_path is not None:
        sample_pdf_path = pathlib.Path(str(sample_pdf_path))
    if not isinstance(sample_md_path, pathlib.Path) and sample_md_path is not None:
        sample_md_path = pathlib.Path(str(sample_md_path))

    mock_page = create_mock_page(sample_md_path.with_suffix('').name)

    mock_context = MagicMock()
    mock_context.assets_dir = 'assets'
    mock_context.node = mock_page
    mock_context.page_index = mock_page.index
    mock_context.page_name = mock_page.name
    mock_context.page_node_id = mock_page.node_id
    mock_context.page_route = mock_page.route
    mock_context.safe_filename_base = mock_page.name
    mock_context.output_md_document = MagicMock(spec=MarkdownDocument)

    pretend_output_dir_handler = TemporaryFilePath(suffix='', prefix='tmp')
    temp_working_dir_handler = TemporaryFilePath(suffix='', prefix='tmp')

    def mock_context__enter__(_):
        pretend_output_dir = pretend_output_dir_handler.__enter__()
        mock_context.output_dir = pretend_output_dir
        pretend_output_dir.mkdir()

        pretend_assets_dir = pretend_output_dir / pathlib.Path(mock_context.assets_dir)
        pretend_assets_dir.mkdir()
        mock_context.output_assets_dir_path = pretend_assets_dir

        temp_working_dir = temp_working_dir_handler.__enter__()
        mock_context.temp_working_dir = temp_working_dir
        temp_working_dir.mkdir()

        if sample_pdf_path is not None:
            test_run_sample_pdf_path = temp_working_dir / sample_pdf_path.name
            shutil.copy2(sample_pdf_path, test_run_sample_pdf_path)
            mock_context.page_as_pdf_document = PdfDocument(test_run_sample_pdf_path)

        if sample_docx_path is not None:
            # y? is anyone using this?
            test_run_sample_docx_path = temp_working_dir / sample_docx_path.name
            shutil.copy2(sample_docx_path, test_run_sample_docx_path)

        if sample_md_path is not None:
            test_run_sample_md_path = pretend_output_dir / sample_md_path.name
            shutil.copy2(sample_md_path, test_run_sample_md_path)
            mock_context.output_md_path = test_run_sample_md_path

            mock_context.output_md_document = MarkdownDocument.import_md_file(test_run_sample_md_path)

        return mock_context

    def mock_context__exit__(_, exc_type, exc_val, exc_tb):
        try:
            del mock_context.page_as_pdf_document
        finally:
            try:
                shutil.rmtree(mock_context.temp_working_dir)
                temp_working_dir_handler.__exit__(exc_type, exc_val, exc_tb)
            finally:
                try:
                    shutil.rmtree(mock_context.output_assets_dir_path)
                    shutil.rmtree(mock_context.output_dir)
                finally:
                    pretend_output_dir_handler.__exit__(exc_type, exc_val, exc_tb)

    mock_context.__enter__ = mock_context__enter__
    mock_context.__exit__ = mock_context__exit__

    return mock_context

class SeededMockOneNotePageExportTaskContext(OneNotePageExportTaskContext):
    def __init__(self,
                 sample_mhtml_path: Optional[Pathlike] = None,
                 sample_pdf_path: Optional[Pathlike] = None,
                 ):
        mock_page = create_mock_page(
            sample_mhtml_path.with_suffix('').name,
            sample_mhtml_path=sample_mhtml_path,
            sample_pdf_path=sample_pdf_path,
        )

        inner_context = OneNoteExportTaskContext(
            node=mock_page,
            output_dir=MagicMock(spec=pathlib.Path),
            assets_dir=MagicMock(spec=pathlib.Path),
            safe_filename_base=pathlib.Path(mock_page.name),
        )

        self._temp_output_dir_handler = TemporaryFilePath()

        super().__init__(inner_context, create_output_md_document=self._create_output_md_document)

    def _create_output_md_document(self, _: OneNotePageExportTaskContext) -> MarkdownDocument:
        md_path = self._output_dir / self.safe_filename_base.with_suffix('.md')
        self._output_md_path = md_path

        def get_initial_ast():
            export_in_vivo = self._temp_mhtml_export
            with export_in_vivo:
                return self.page_as_pandoc_ast_json

        doc = MarkdownDocument.open_document_ast_json_str(
            initial_document_ast_json=get_initial_ast,
            output_md_path=md_path,
        )
        return doc

    def __enter__(self) -> OneNotePageExportTaskContext:
        self._output_dir = self._temp_output_dir_handler.__enter__()
        super().__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            super().__exit__(exc_type, exc_val, exc_tb)
        finally:
            self._temp_output_dir_handler.__exit__(exc_type, exc_val, exc_tb)
