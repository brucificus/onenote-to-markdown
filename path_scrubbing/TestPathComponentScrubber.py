import unittest

from .PathComponentScrubber import PathComponentScrubber


class TestPathComponentScrubber(unittest.TestCase):
    param_list = [
        ('6/2/2014 8:04 AM Office Lens', '201406020804 Office Lens'),
        ('+Checklist', '+Checklist'),
        ('2019_08_19 4_01 PM Office Lens', '201908191601 Office Lens'),
        ('2"x4"N - Src 1', '2”x4”N - Src 1'),
        ('OCL: Diag: Lumber', 'OCL — Diag — Lumber'),
        ('"Something funny happened"', '“Something funny happened”'),
        ('Plywood 3/4"', 'Plywood 3∕4”'),
        ('**My favorite page**', '＊＊My favorite page＊＊'),
        ('That is the question?', 'That is the question？'),
        ('All | these | worlds', 'All ｜ these ｜ worlds'),
    ]

    def test_path_component_cleanup_returns_expected(self):
        for input, expected in self.param_list:
            with self.subTest(input=input, expected=expected):
                # Arrange
                subject = PathComponentScrubber()

                # Act
                actual = subject.cleanup_path_component(input).name

                # Assert
                self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
