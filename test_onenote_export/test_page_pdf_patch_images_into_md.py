import logging
import pathlib
import unittest
from unittest.mock import MagicMock

from onenote_export.page_pdf_patch_images_into_md import page_pdf_patch_images_into_md
from .seeded_fake_onenote_page_export_task_context import create_seeded_fake_onenote_page_export_task_context


class TestPagePdfPatchImagesIntoMd(unittest.TestCase):

    def test_can_run_against_samples_without_error(self):
        sample_data_dir = pathlib.Path(__file__).parent / pathlib.Path('sample_data')
        sample_document_names = {f.with_suffix('').name for f in sample_data_dir.glob('*.md')}

        for sample_document_name in sample_document_names:
            with self.subTest(sample_document_name=sample_document_name):
                with create_seeded_fake_onenote_page_export_task_context(
                    sample_docx_path=sample_data_dir / pathlib.Path(f'{sample_document_name}.docx'),
                    sample_pdf_path=sample_data_dir / pathlib.Path(f'{sample_document_name}.pdf'),
                    sample_md_path=sample_data_dir / pathlib.Path(f'{sample_document_name}.md'),
                ) as context:
                    page_pdf_patch_images_into_md(context, MagicMock(logging.Logger))
                    self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
