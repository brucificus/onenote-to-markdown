import fitz
import pathlib
import unittest
from unittest.mock import Mock, MagicMock, patch, mock_open

from onenote import OneNotePage
from onenote_export.OneNoteExportMiddlewareContext import OneNoteExportMiddlewareContext
from onenote_export.OneNotePageExporter import OneNotePageExporter


class TestOneNotePageExporter(unittest.TestCase):
    def test_can_instantiate(self):
        # Arrange
        subject_ctor_args = ()
        subject_ctor_kwargs = {}

        # Act
        actual = OneNotePageExporter(*subject_ctor_args, **subject_ctor_kwargs)

        # Assert
        self.assertIsInstance(actual, OneNotePageExporter)

    @patch('os.path.exists', lambda _: None)
    @patch('os.makedirs', lambda _, exist_ok: None)
    @patch('os.remove', lambda _: None)
    @patch('fitz.Document.__new__', MagicMock())
    @patch('fitz.Pixmap', lambda _, __: fitz.Pixmap())
    @patch('onenote_export.OneNotePageExporter.open', mock_open(read_data='some data'))
    @patch('shutil.move', lambda _, __: None)
    def test_can_invoke_without_exception(self):
        # Arrange
        context_param = self._create_middleware_context()
        next_middleware_param = lambda _: None
        subject = self._create_subject_with_mocked_dependencies()

        # Act
        actual = subject(context_param, next_middleware_param)

        # Assert
        self.assertEqual(actual, None)

    @staticmethod
    def _create_middleware_context():
        node = TestOneNotePageExporter._create_onenote_page()
        context_param = OneNoteExportMiddlewareContext(
            node,
            MagicMock(spec=pathlib.Path),  # output_dir
            MagicMock(spec=pathlib.Path),  # assets_dir
            lambda _: MagicMock(spec=pathlib.Path),  # convert_node_name_to_path_component
        )
        return context_param

    @staticmethod
    def _create_onenote_page():
        node = Mock(
            spec=OneNotePage,
            export_docx=lambda _: None,
            export_pdf=lambda _: None,
        )
        return node

    @staticmethod
    def _create_subject_with_mocked_dependencies() -> OneNotePageExporter:
        subject_ctor_args = ()
        subject_ctor_kwargs = {
            'os_system': lambda _: None,
        }

        return OneNotePageExporter(*subject_ctor_args, **subject_ctor_kwargs)


if __name__ == '__main__':
    unittest.main()
