import unittest

from onenote_export.OneNoteExportMiddlewareDispatcher import OneNoteExportMiddlewareDispatcher


class TestOneNoteExportMiddlewareDispatcher(unittest.TestCase):
    def test_can_instantiate(self):
        # Arrange
        subject_ctor_args = (
            None,  # combine_returns
            None,  # middleware_context_factory
        )
        subject_ctor_kwargs = {
            'middlewares_by_type': {},
            'simple_middleware_factory': None,
            'traverse_children_depth_first': True,
        }

        # Act
        actual = OneNoteExportMiddlewareDispatcher(*subject_ctor_args, **subject_ctor_kwargs)

        # Assert
        self.assertIsInstance(actual, OneNoteExportMiddlewareDispatcher)


if __name__ == '__main__':
    unittest.main()
