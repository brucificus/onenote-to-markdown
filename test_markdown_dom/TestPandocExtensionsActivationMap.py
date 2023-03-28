import unittest

from markdown_dom.PandocExtensionActivationMap import PandocExtensionActivationMap
from markdown_dom.PandocExtension import PandocExtension


class TestPandocExtensionsActivationMap(unittest.TestCase):
    def test_can_instantiate(self):
        actual = PandocExtensionActivationMap()

        self.assertIsInstance(actual, PandocExtensionActivationMap)

    def test_can_from_str(self):
        # Arrange
        input_str = '+compact_definition_lists-fancy_lists-citations'
        expected = {
            PandocExtension.compact_definition_lists: True,
            PandocExtension.fancy_lists: False,
            PandocExtension.citations: False,
        }

        # Act
        actual = PandocExtensionActivationMap.from_str(input_str)

        # Assert
        self.assertIsInstance(actual, PandocExtensionActivationMap)
        self.assertEqual(actual, PandocExtensionActivationMap(expected))

    def test_can_str(self):
        # Arrange
        input_dict = {
            PandocExtension.compact_definition_lists: True,
            PandocExtension.fancy_lists: False,
            PandocExtension.citations: False,
        }
        expected = '-citations+compact_definition_lists-fancy_lists'
        subject = PandocExtensionActivationMap(input_dict)

        # Act
        actual = str(subject)

        # Assert
        self.assertIsInstance(actual, str)
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
