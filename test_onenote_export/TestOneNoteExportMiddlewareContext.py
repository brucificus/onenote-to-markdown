import unittest

from onenote_export.OneNoteExportMiddlewareContext import OneNoteExportMiddlewareContext


class TestOneNoteExportMiddlewareContext(unittest.TestCase):
    def test_can_instantiate(self):
        # Arrange
        subject_ctor_args = (
            None,  # node
            None,  # output_dir
            None,  # assets_dir
            None,  # convert_node_name_to_path_component
        )
        subject_ctor_kwargs = {
        }

        # Act
        actual = OneNoteExportMiddlewareContext(*subject_ctor_args, **subject_ctor_kwargs)

        # Assert
        self.assertIsInstance(actual, OneNoteExportMiddlewareContext)


if __name__ == '__main__':
    unittest.main()
