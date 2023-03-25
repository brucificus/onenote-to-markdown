import unittest

from onenote_export.OneNoteExporter import OneNoteExporter, create_default_onenote_exporter


class TestOneNoteExporter(unittest.TestCase):
    def test_can_instantiate(self):
        # Arrange
        subject_ctor_args = (
            None,  # task_factory: OneNoteExportTaskFactory
        )
        subject_ctor_kwargs = {}

        # Act
        actual = OneNoteExporter(*subject_ctor_args, **subject_ctor_kwargs)

        # Assert
        self.assertIsInstance(actual, OneNoteExporter)

    def test_create_default_onenote_exporter_can_return_instance(self):
        # Arrange
        factory_args = (
            None,  # root_output_dir
            None,  # page_relative_assets_dir
            None,  # path_component_scrubber
            lambda n: True,  # should_export
        )
        factory_kwargs = {}

        # Act
        actual = create_default_onenote_exporter(*factory_args, **factory_kwargs)

        # Assert
        self.assertIsInstance(actual, OneNoteExporter)


if __name__ == '__main__':
    unittest.main()
