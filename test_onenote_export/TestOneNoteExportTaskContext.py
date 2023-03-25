import unittest

from onenote_export.OneNoteExportTaskContext import OneNoteExportTaskContext


class TestOneNoteExportTaskContext(unittest.TestCase):
    def test_can_instantiate(self):
        # Arrange
        subject_ctor_args = (
            None,  # node
            None,  # output_dir
            None,  # assets_dir
            None,  # safe_filename_base
        )
        subject_ctor_kwargs = {
        }

        # Act
        actual = OneNoteExportTaskContext(*subject_ctor_args, **subject_ctor_kwargs)

        # Assert
        self.assertIsInstance(actual, OneNoteExportTaskContext)


if __name__ == '__main__':
    unittest.main()
