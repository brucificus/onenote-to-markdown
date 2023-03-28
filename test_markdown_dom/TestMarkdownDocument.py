import pathlib
import shutil
import unittest
from typing import Callable, Optional

import panflute

from markdown_dom.MarkdownDocument import MarkdownDocument
from onenote_export.temporary_file import TemporaryFilePath


class TestMarkdownDocument(unittest.TestCase):
    def test_can_instantiate_from_sample_ast_json_without_error(self):
        def can_instantiate(document_ast_json: str):
            # Arrange
            with TemporaryFilePath(suffix='.md') as temp_output_md_file:
                ctor_kwargs = {
                    'initial_document_ast_json': document_ast_json,
                    'output_md_path': temp_output_md_file,
                }

                # Act
                actual = MarkdownDocument(**ctor_kwargs)

                # Assert
                self.assertIsInstance(actual, MarkdownDocument)

        self._subtest_for_each_sample_document_ast_json(can_instantiate)

    def test_can_import_sample_md_file_without_error(self):
        def can_instantiate(md_file: pathlib.Path):
            # Arrange
            import_kwargs = {
                'input_md_path': md_file,
            }

            # Act
            actual = MarkdownDocument.import_md_file(**import_kwargs)

            # Assert
            self.assertIsInstance(actual, MarkdownDocument)

        self._subtest_for_each_sample_markdown_document(can_instantiate)

    def _prepare_filter(self, doc: panflute.Doc) -> None:
        self.assertIsInstance(doc, panflute.Doc)
        self.assertIsNotNone(doc.content)
        self.assertNotEqual(len(doc.content), 0)

    def _element_filter(self, element: panflute.Element, doc: panflute.Doc) -> Optional[panflute.Element]:
        self.assertIsInstance(element, panflute.Element)
        if type(element) == panflute.Link:
            el: panflute.Link = element
            el.url = ''
        self.assertIsInstance(doc, panflute.Doc)

    def _finalize_filter(self, doc: panflute.Doc) -> None:
        self.assertIsInstance(doc, panflute.Doc)
        self.assertIsNotNone(doc.content)
        self.assertNotEqual(len(doc.content), 0)

    def _stop_if(self, element: panflute.Element) -> bool:
        self.assertIsInstance(element, panflute.Element)
        return False

    def test_can_run_filters_on_sample_ast_json_without_error(self):
        def can_be_filtered(document_ast_json: str):
            # Arrange
            with TemporaryFilePath(suffix='.md') as temp_output_md_file:
                ctor_kwargs = {
                    'initial_document_ast_json': document_ast_json,
                    'output_md_path': temp_output_md_file,
                }
                subject = MarkdownDocument(**ctor_kwargs)

                # Act
                subject.update_via_panflute_filter(
                    prepare_filter=self._prepare_filter,
                    element_filter=self._element_filter,
                    finalize_filter=self._finalize_filter,
                    stop_if=self._stop_if,
                )

                # Assert
                self.assertTrue(True)

        self._subtest_for_each_sample_document_ast_json(can_be_filtered)

    def _subtest_for_each_sample_markdown_document(self, func: Callable[[pathlib.Path], None]):
        sample_data_dir = pathlib.Path(__file__).parent / pathlib.Path('sample_data')
        sample_document_paths = sample_data_dir.glob('*.md')

        for sample_document_path in sample_document_paths:
            with self.subTest(sample_document_name=sample_document_path.name):
                with TemporaryFilePath(suffix='.md') as temp_file:
                    shutil.copy2(sample_document_path, temp_file)
                    func(temp_file)

    def _subtest_for_each_sample_document_ast_json(self, func: Callable[[str], None]):
        sample_data_dir = pathlib.Path(__file__).parent / pathlib.Path('sample_data')
        sample_file_paths = set(sample_data_dir.glob('*.json'))
        assert len(sample_file_paths) > 0

        for sample_file in sample_file_paths:
            with self.subTest(sample_document_name=sample_file.name):
                with open(sample_file, 'r') as f:
                    func(f.read())


if __name__ == '__main__':
    unittest.main()
