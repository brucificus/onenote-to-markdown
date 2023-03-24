import unittest

from path_scrubbing.DateDigitsSubstitutionFactory import DateDigitsSubstitutionFactory


class TestDateDigitsSubstitutionFactory(unittest.TestCase):
    param_list = [
        {
            "old_sep": '/',
            "new_sep": '-',
            "abbrev_year": False,
            "input_date_component_order": 'mdy',
            "input_path_component": '01/02/2023',
            "output_date_component_order": 'ymd',
            "expected": '2023-01-02',
        },
        {
            "old_sep": '_',
            "new_sep": '-',
            "abbrev_year": False,
            "input_date_component_order": 'mdy',
            "input_path_component": '01_02_2023',
            "output_date_component_order": 'ymd',
            "expected": '2023-01-02',
        },
        {
            "old_sep": '-',
            "new_sep": '-',
            "abbrev_year": False,
            "input_date_component_order": 'ymd',
            "input_path_component": '2017-7-11',
            "output_date_component_order": 'ymd',
            "expected": '2017-07-11',
        },
        {
            "old_sep": '/',
            "new_sep": '-',
            "abbrev_year": False,
            "input_date_component_order": 'mdy',
            "input_path_component": '7/11/2017',
            "output_date_component_order": 'ymd',
            "expected": '2017-07-11',
        },
    ]

    def test_given_params_can_create_substitutor_which_returns_expected(self):
        for param_set in self.param_list:
            with self.subTest(**param_set):
                # Arrange
                old_sep = param_set['old_sep']
                new_sep = param_set['new_sep']
                abbrev_year = param_set['abbrev_year']
                input_date_component_order = param_set['input_date_component_order']
                input_path_component = param_set['input_path_component']
                output_date_component_order = param_set['output_date_component_order']
                expected = param_set['expected']

                subject = DateDigitsSubstitutionFactory(old_sep, date_component_order=input_date_component_order, abbrev_year=abbrev_year)
                substitutor = subject.create_substitutor(new_date_components_sep=new_sep, new_date_component_order=output_date_component_order)

                # Act
                actual = substitutor(input_path_component)

                # Assert
                self.assertEqual(expected, actual)
