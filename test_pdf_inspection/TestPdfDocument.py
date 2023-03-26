import pathlib
import shutil
import unittest
from typing import Callable

from onenote_export.temporary_file import TemporaryFilePath
from pdf_inspection.PdfDocument import PdfDocument
from pdf_inspection.PdfDocumentPage import PdfDocumentPage
from pdf_inspection.PdfDocumentPageDrawing import PdfDocumentPageDrawing
from pdf_inspection.PdfDocumentPageImage import PdfDocumentPageImage


class TestPdfDocument(unittest.TestCase):
    def test_can_instantiate_from_samples_without_error(self):
        def can_instantiate(temp_file: pathlib.Path):
            # Arrange & Act
            actual = PdfDocument(temp_file)

            self.assertIsInstance(actual, PdfDocument)

        self._subtest_for_each_sample_document(can_instantiate)

    def test_can_enumerate_pages_from_samples_without_error(self):
        def can_enumerate_pages(temp_file: pathlib.Path):
            # Arrange
            subject = PdfDocument(temp_file)

            # Act
            actual = list(subject.pages)

            # Assert
            self.assertIsInstance(actual, list)
            self.assertNotEqual(len(actual), 0)
            for page in actual:
                self.assertIsInstance(page, PdfDocumentPage)

        self._subtest_for_each_sample_document(can_enumerate_pages)

    def test_can_enumerate_page_images_from_samples_without_error(self):
        def can_enumerate_page_images(temp_file: pathlib.Path):
            # Arrange
            subject = PdfDocument(temp_file)
            for page in subject.pages:
                with self.subTest(page=page):

                    # Act
                    actual = list(page.images)

                    # Assert
                    self.assertIsInstance(actual, list)
                    for image in actual:
                        self.assertIsInstance(image, PdfDocumentPageImage)

        self._subtest_for_each_sample_document(can_enumerate_page_images)

    def test_can_enumerate_page_drawings_from_samples_without_error(self):
        def can_enumerate_page_drawings(temp_file: pathlib.Path):
            # Arrange
            subject = PdfDocument(temp_file)
            for page in subject.pages:
                with self.subTest(page=page):

                    # Act
                    actual = list(page.drawings)

                    # Assert
                    self.assertIsInstance(actual, list)
                    for drawing in actual:
                        self.assertIsInstance(drawing, PdfDocumentPageDrawing)

        self._subtest_for_each_sample_document(can_enumerate_page_drawings)

    def test_can_export_page_images_from_samples_without_error(self):
        def can_instantiate(temp_file: pathlib.Path):
            # Arrange
            subject = PdfDocument(temp_file)
            for page in subject.pages:
                with self.subTest(page=page):
                    for image in page.images:
                        with self.subTest(image=image):
                            with TemporaryFilePath(suffix='.png') as temp_png_file:

                                # Act
                                image.export_png(temp_png_file)

                                # Assert
                                self.assertTrue(temp_png_file.exists())

        self._subtest_for_each_sample_document(can_instantiate)

    def _subtest_for_each_sample_document(self, func: Callable[[pathlib.Path], None]):
        sample_data_dir = pathlib.Path(__file__).parent / pathlib.Path('sample_data')
        assert sample_data_dir.exists()
        sample_document_paths = sample_data_dir.glob('*.pdf')

        for sample_document_path in sample_document_paths:
            with self.subTest(sample_document_name=sample_document_path.name):
                with TemporaryFilePath() as temp_holding_dir:
                    temp_holding_dir.mkdir()
                    temp_file = temp_holding_dir / sample_document_path.name
                    shutil.copy(sample_document_path, temp_file)
                    func(temp_file)


if __name__ == '__main__':
    unittest.main()
