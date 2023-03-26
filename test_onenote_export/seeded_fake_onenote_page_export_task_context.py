import pathlib
import shutil
from unittest.mock import MagicMock

from fitz import fitz

from onenote.OneNotePage import OneNotePage
from onenote_export.Pathlike import Pathlike
from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext
from onenote_export.temporary_file import TemporaryFilePath


def create_seeded_fake_onenote_page_export_task_context(
    sample_docx_path: Pathlike,
    sample_pdf_path: Pathlike,
    sample_md_path: Pathlike
) -> OneNotePageExportTaskContext:
    if not isinstance(sample_docx_path, pathlib.Path):
        sample_docx_path = pathlib.Path(str(sample_docx_path))
    if not isinstance(sample_pdf_path, pathlib.Path):
        sample_pdf_path = pathlib.Path(str(sample_pdf_path))
    if not isinstance(sample_md_path, pathlib.Path):
        sample_md_path = pathlib.Path(str(sample_md_path))

    mock_page = MagicMock(spec=OneNotePage)
    mock_page.children = ()
    mock_page.name = sample_md_path.with_suffix('').name
    mock_page.parent = None

    mock_context = MagicMock()
    mock_context.assets_dir = 'assets'
    mock_context.node = mock_page
    mock_context.page_index = mock_page.index
    mock_context.page_name = mock_page.name
    mock_context.page_node_id = mock_page.node_id
    mock_context.page_route = mock_page.route
    mock_context.safe_filename_base = mock_page.name

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

        test_run_sample_pdf_path = temp_working_dir / sample_pdf_path.name
        shutil.copy2(sample_pdf_path, test_run_sample_pdf_path)
        mock_context.pymupdf_document = fitz.open(str(test_run_sample_pdf_path))

        # y? is anyone using this?
        test_run_sample_docx_path = temp_working_dir / sample_docx_path.name
        shutil.copy2(sample_docx_path, test_run_sample_docx_path)

        test_run_sample_md_path = pretend_output_dir / sample_md_path.name
        shutil.copy2(sample_md_path, test_run_sample_md_path)
        mock_context.output_md_path = test_run_sample_md_path

        return mock_context

    def mock_context__exit__(_, exc_type, exc_val, exc_tb):
        try:
            mock_context.pymupdf_document.close()
            del mock_context.pymupdf_document
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
