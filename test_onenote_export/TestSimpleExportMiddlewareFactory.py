import unittest
from typing import Callable

from onenote_export.SimpleOneNoteExportMiddlewareFactory import SimpleOneNoteExportMiddlewareFactory


class TestSimpleExportMiddlewareFactory(unittest.TestCase):
    def test_join_given_simple_params_returns_callable_callable(self):
        # Arrange
        subject = SimpleOneNoteExportMiddlewareFactory()

        # Act
        actual = subject.chain(middlewares=())

        # Assert
        self.assertIsInstance(actual, Callable)

    def test_before_given_simple_params_returns_callable_callable(self):
        # Arrange
        subject = SimpleOneNoteExportMiddlewareFactory()

        # Act
        actual = subject.before(action=lambda: None)

        # Assert
        self.assertIsInstance(actual, Callable)

    def test_preempt_given_simple_params_returns_callable_callable(self):
        # Arrange
        subject = SimpleOneNoteExportMiddlewareFactory()

        # Act
        actual = subject.preempt(action=lambda: None)

        # Assert
        self.assertIsInstance(actual, Callable)

    def test_either_or_given_simple_params_returns_callable_callable(self):
        # Arrange
        subject = SimpleOneNoteExportMiddlewareFactory()

        # Act
        actual = subject.either_or(condition=lambda: None, middleware_if=lambda: None, middleware_else=lambda: None)

        # Assert
        self.assertIsInstance(actual, Callable)


if __name__ == '__main__':
    unittest.main()
