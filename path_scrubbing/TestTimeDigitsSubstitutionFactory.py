import unittest

from .TimeDigitsSubstitutionFactory import TimeDigitsSubstitutionFactory


class TestTimeDigitsSubstitutionFactory(unittest.TestCase):
    create_substitutor_replacing_separator_param_list = [
        # twelve_hour = True
        dict(  # expect_seconds=True, include_missing_seconds=False
            expect_seconds=True,
            twelve_hour=True,
            include_missing_seconds=False,
            input='4:31:22 AM',
            expected='04:31:22 AM'
        ),
        dict(  # expect_seconds=False, include_missing_seconds=False
            expect_seconds=False,
            include_missing_seconds=False,
            twelve_hour=True,
            input='5:33 AM',
            expected='05:33 AM'
        ),
        dict(  # expect_seconds=False, include_missing_seconds=True
            expect_seconds=False,
            include_missing_seconds=True,
            twelve_hour=True,
            input='7:37 PM',
            expected='07:37:00 PM'
        ),

        # twelve_hour=False
        dict(  # expect_seconds=True, include_missing_seconds=False
            expect_seconds=True,
            twelve_hour=False,
            include_missing_seconds=False,
            input='4:31:22',
            expected='04:31:22'
        ),
        dict(  # expect_seconds=False, include_missing_seconds=False
            expect_seconds=False,
            include_missing_seconds=False,
            twelve_hour=False,
            input='5:33',
            expected='05:33'
        ),
        dict(  # expect_seconds=False, include_missing_seconds=True
            expect_seconds=False,
            include_missing_seconds=True,
            twelve_hour=False,
            input='19:37',
            expected='19:37:00'
        ),
    ]

    def test_given_params_can_create_substitutor_replacing_separator_which_returns_expected(self):
        for param_set in self.create_substitutor_replacing_separator_param_list:
            with self.subTest(**param_set):
                # Arrange
                old_sep = ':'
                expect_seconds = param_set['expect_seconds']
                twelve_hour = param_set['twelve_hour']
                new_sep = ':'
                include_missing_seconds = param_set['include_missing_seconds']
                input = param_set['input']
                expected = param_set['expected']
                subject = TimeDigitsSubstitutionFactory(old_sep, expect_seconds=expect_seconds, twelve_hour=twelve_hour)
                substitutor = subject.create_substitutor_replacing_separator(new_time_components_sep=new_sep, include_missing_seconds=include_missing_seconds)

                # Act
                actual = substitutor(input)

                # Assert
                self.assertEqual(expected, actual)

    create_substitutor_coercing_to_24hr_iso8601_param_list = [
        # twelve_hour = True
        dict(  # expect_seconds=True, include_missing_seconds=False
            expect_seconds=True,
            twelve_hour=True,
            include_missing_seconds=False,
            input='4:31:22 AM',
            expected='04:31:22'
        ),
        dict(  # expect_seconds=False, include_missing_seconds=False
            expect_seconds=False,
            include_missing_seconds=False,
            twelve_hour=True,
            input='5:33 AM',
            expected='05:33'
        ),
        dict(  # expect_seconds=False, include_missing_seconds=True
            expect_seconds=False,
            include_missing_seconds=True,
            twelve_hour=True,
            input='7:37 PM',
            expected='19:37:00'
        ),

        # twelve_hour=False
        dict(  # expect_seconds=True, include_missing_seconds=False
            expect_seconds=True,
            twelve_hour=False,
            include_missing_seconds=False,
            input='4:31:22',
            expected='04:31:22'
        ),
        dict(  # expect_seconds=False, include_missing_seconds=False
            expect_seconds=False,
            include_missing_seconds=False,
            twelve_hour=False,
            input='5:33',
            expected='05:33'
        ),
        dict(  # expect_seconds=False, include_missing_seconds=True
            expect_seconds=False,
            include_missing_seconds=True,
            twelve_hour=False,
            input='19:37',
            expected='19:37:00'
        ),
    ]

    def test_given_params_can_create_substitutor_coercing_to_24hr_iso8601_which_returns_expected(self):
        for param_set in self.create_substitutor_coercing_to_24hr_iso8601_param_list:
            with self.subTest(**param_set):
                # Arrange
                old_sep = ':'
                expect_seconds = param_set['expect_seconds']
                twelve_hour = param_set['twelve_hour']
                include_missing_seconds = param_set['include_missing_seconds']
                input = param_set['input']
                expected = param_set['expected']
                subject = TimeDigitsSubstitutionFactory(old_sep, expect_seconds=expect_seconds, twelve_hour=twelve_hour)
                substitutor = subject.create_substitutor_coercing_to_24hr_iso8601(include_missing_seconds=include_missing_seconds)

                # Act
                actual = substitutor(input)

                # Assert
                self.assertEqual(expected, actual)
