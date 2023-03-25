import fitz
import pathlib
import unittest
from unittest.mock import MagicMock, patch, mock_open

from onenote import OneNotePage, OneNoteSection, OneNoteSectionGroup, OneNoteNotebook, OneNoteApplication
from onenote_export.OneNoteExportTaskContext import OneNoteExportTaskContext
from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext
from onenote_export.OneNotePageExporter import OneNotePageExporter
from onenote_export.TemporaryOneNotePageDocxExport import TemporaryOneNotePageDocxExport
from onenote_export.TemporaryOneNotePagePdfExport import TemporaryOneNotePagePdfExport
from path_scrubbing import PathComponentScrubber


class TestOneNotePageExporter(unittest.TestCase):
    def test_can_instantiate(self):
        # Arrange
        subject_ctor_args = (self._mock_context(), ())
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
        subject = self._create_subject_with_mocked_dependencies()

        # Act
        actual = subject()

        # Assert
        self.assertEqual(actual, None)

    def _mock_context(self) -> OneNotePageExportTaskContext:
        page_node = self._mock_onenote_page()
        mock_output_dir = MagicMock(spec=pathlib.Path)
        mock_assets_dir = MagicMock(spec=pathlib.Path)
        mock_path_component_scrubber = MagicMock(spec=PathComponentScrubber)
        basis_context = OneNoteExportTaskContext(
            page_node,
            mock_output_dir,  # output_dir
            mock_assets_dir,  # assets_dir
            mock_path_component_scrubber,  # path_component_scrubber
        )
        context_param = OneNotePageExportTaskContext(
            basis_context,
            create_temporary_pdf_export_handler=lambda _: MagicMock(spec=TemporaryOneNotePagePdfExport),
            create_temporary_docx_export_handler=lambda _: MagicMock(spec=TemporaryOneNotePageDocxExport),
        )
        return context_param

    def _mock_onenote_page(self) -> OneNotePage:
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

    def _create_subject_with_mocked_dependencies(self) -> OneNotePageExporter:
        subject_ctor_args = ()
        subject_ctor_kwargs = {'context': self._mock_context(), 'prerequisites': ()}

        return OneNotePageExporter(*subject_ctor_args, **subject_ctor_kwargs)


if __name__ == '__main__':
    unittest.main()
