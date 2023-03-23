import fitz
import pathlib
import unittest
from unittest.mock import Mock, MagicMock, patch, mock_open

from onenote import OneNotePage, OneNoteSection, OneNoteSectionGroup, OneNoteNotebook, OneNoteApplication
from onenote_export.OneNoteExportMiddlewareContext import OneNoteExportMiddlewareContext
from onenote_export.OneNotePageExportMiddlewareContext import OneNotePageExportMiddlewareContext
from onenote_export.OneNotePageExporter import OneNotePageExporter
from onenote_export.TemporaryOneNotePageDocxExport import TemporaryOneNotePageDocxExport
from onenote_export.TemporaryOneNotePagePdfExport import TemporaryOneNotePagePdfExport


class TestOneNotePageExporter(unittest.TestCase):
    def test_can_instantiate(self):
        # Arrange
        subject_ctor_args = ()
        subject_ctor_kwargs = {}

        # Act
        actual = OneNotePageExporter(*subject_ctor_args, **subject_ctor_kwargs)

        # Assert
        self.assertIsInstance(actual, OneNotePageExporter)

    @patch('onenote_export.TemporaryOneNotePageDocxExport', MagicMock(spec=TemporaryOneNotePageDocxExport))
    @patch('onenote_export.TemporaryOneNotePagePdfExport', MagicMock(spec=TemporaryOneNotePagePdfExport))
    @patch('fitz.Document.__new__', MagicMock())
    @patch('fitz.Pixmap', lambda _, __: fitz.Pixmap())
    @patch('onenote_export.OneNotePageExporter.open', mock_open(read_data='some data'))
    @patch('os.makedirs', lambda _, exist_ok: None)
    @patch('os.path.exists', lambda _: None)
    @patch('os.remove', lambda _: None)
    @patch('shutil.move', lambda _, __: None)
    def test_can_invoke_without_exception(self):
        # Arrange
        context_param = self._mock_middleware_context()
        next_middleware_param = lambda _: None
        subject = self._create_subject_with_mocked_dependencies()

        # Act
        actual = subject(context_param, next_middleware_param)

        # Assert
        self.assertEqual(actual, None)

    @staticmethod
    def _mock_middleware_context() -> OneNotePageExportMiddlewareContext:
        page_node = TestOneNotePageExporter._mock_onenote_page()
        mock_output_dir = MagicMock(spec=pathlib.Path)
        mock_assets_dir = MagicMock(spec=pathlib.Path)
        mock_path_component_scrubber = lambda _: MagicMock(spec=pathlib.Path)
        basis_context = OneNoteExportMiddlewareContext(
            page_node,
            mock_output_dir,  # output_dir
            mock_assets_dir,  # assets_dir
            mock_path_component_scrubber,  # convert_node_name_to_path_component
        )
        context_param = OneNotePageExportMiddlewareContext(
            basis_context,
            create_temporary_pdf_export_handler=lambda _: MagicMock(spec=TemporaryOneNotePagePdfExport),
            create_temporary_docx_export_handler=lambda _: MagicMock(spec=TemporaryOneNotePageDocxExport),
        )
        return context_param

    @staticmethod
    def _mock_onenote_page() -> OneNotePage:
        application_node = MagicMock(spec=OneNoteApplication)
        application_node.parent = None

        notebook_node = MagicMock(spec=OneNoteNotebook)
        notebook_node.parent = application_node
        notebook_node.name = 'some notebook name'

        section_group_node = MagicMock(spec=OneNoteSectionGroup)
        section_group_node.parent = notebook_node
        section_group_node.name = 'some section group name'

        section_node = MagicMock(spec=OneNoteSection)
        section_node.parent = section_group_node
        section_node.name = 'some section name'

        page_node = MagicMock(spec=OneNotePage)
        page_node.parent = section_node
        page_node.name = 'some page name'

        return page_node

    @staticmethod
    def _create_subject_with_mocked_dependencies() -> OneNotePageExporter:
        subject_ctor_args = ()
        subject_ctor_kwargs = {}

        return OneNotePageExporter(*subject_ctor_args, **subject_ctor_kwargs)


if __name__ == '__main__':
    unittest.main()
