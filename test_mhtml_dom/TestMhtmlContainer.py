import pathlib
import unittest

from mhtml_dom.MhtmlContainer import MhtmlContainer


class TestMhtmlContainer(unittest.TestCase):
    def test_can_read_file_without_exceptions(self):
        sample_data_dir = pathlib.Path(__file__).parent / pathlib.Path('sample_data')
        sample_files = set(sample_data_dir.glob('*.mht'))

        for sample_file in sample_files:
            with self.subTest(sample_file_name=sample_file.name):
                container = MhtmlContainer.read_file(sample_file)
                self.assertIsInstance(container, MhtmlContainer)
                self.assertGreater(len(container.content_items), 0)


if __name__ == '__main__':
    unittest.main()
