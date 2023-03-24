import functools
import pathlib
import unittest

from onenote_export.OneNoteExportMiddlewareContext import OneNoteExportMiddlewareContext
from onenote_export.OneNoteExportMiddlewareContextFactory import OneNoteExportMiddlewareContextFactory


class TestOneNoteExportMiddlewareContextFactory(unittest.TestCase):
    def test_can_instantiate(self):
        # Arrange
        instantiate_subject = self._create_subject_instance

        # Arrange
        actual = instantiate_subject()

        # Assert
        self.assertIsInstance(actual, OneNoteExportMiddlewareContextFactory)

    def test_create_context_for_traversal_transition_to_child_can_return_instance(self):
        # Arrange
        subject_instance = self._create_subject_instance()
        subject_method_args = (
            self._create_traversal_antecedent_context_instance(),  # current_context
            None,  # child
        )
        subject_method_kwargs = {}
        subject_method = functools.partial(subject_instance.create_context_for_traversal_transition_to_child, *subject_method_args, **subject_method_kwargs)

        # Act
        actual = subject_method()

        # Assert
        self.assertIsInstance(actual, OneNoteExportMiddlewareContext)

    def _create_traversal_antecedent_context_instance(self):
        return OneNoteExportMiddlewareContext(
            None,  # node
            pathlib.Path(),  # output_dir
            pathlib.Path(),  # assets_dir
            None,  # convert_node_name_to_path_component
        )

    def _create_subject_instance(self):
        subject_ctor_args = (
            pathlib.Path(),  # root_output_dir
            pathlib.Path(),  # page_relative_assets_dir
            None,  # convert_node_name_to_path_component
        )
        subject_ctor_kwargs = {}

        actual = OneNoteExportMiddlewareContextFactory(*subject_ctor_args, **subject_ctor_kwargs)
        return actual


if __name__ == '__main__':
    unittest.main()
