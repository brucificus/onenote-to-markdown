import logging
import pathlib
import unittest
from unittest.mock import MagicMock

from onenote_export.page_export_tasks.page_remove_onenote_footer import page_remove_onenote_footer
from test_onenote_export.test_page_export_tasks.seeded_fake_onenote_page_export_task_context import \
    SeededMockOneNotePageExportTaskContext


class TestPageRemoveOneNoteFooter(unittest.TestCase):

    def test_can_run_against_samples_without_error(self):
        sample_data_dir = pathlib.Path(__file__).parent / pathlib.Path('sample_data')
        sample_document_names = {f.with_suffix('').name for f in sample_data_dir.glob('*.mht')}

        for sample_document_name in sample_document_names:
            with self.subTest(sample_document_name=sample_document_name):
                with SeededMockOneNotePageExportTaskContext(
                    sample_mhtml_path=sample_data_dir / pathlib.Path(f'{sample_document_name}.mht'),

                ) as context:
                    page_remove_onenote_footer(context, MagicMock(logging.Logger))
                    self.assertTrue(True)



if __name__ == '__main__':
    unittest.main()

