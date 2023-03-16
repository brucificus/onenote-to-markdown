import functools
import re
from datetime import date
from typing import Match, Callable

from .LabeledTextFunc import LabeledTextFunc
from .YearMonthDayDigitsComponentOrder import YearMonthDayDigitsComponentOrder


class DateDigitsSubstitutionFactory:
    def __init__(self,
                 date_components_sep: str,
                 date_component_order: YearMonthDayDigitsComponentOrder = YearMonthDayDigitsComponentOrder.MDY,
                 abbrev_year: bool = False
                 ):
        self._pattern = self._create_regex_pattern(date_components_sep, date_component_order, abbrev_year)
        self._date_components_sep = date_components_sep
        self._date_component_order = date_component_order
        self._abbrev_year = abbrev_year

    @staticmethod
    def _create_regex_pattern(date_components_sep: str, date_component_order: YearMonthDayDigitsComponentOrder, abbrev_year: bool) -> str:
        year_digits_count = 2 if abbrev_year else 4
        if date_component_order == 'ymd':
            return r'\b(\d{' + str(year_digits_count) + '})' + date_components_sep + r'(\d{1,2})' + date_components_sep + r'(\d{1,2})\b'
        elif date_component_order == 'dmy':
            return r'\b(\d{1,2})' + date_components_sep + r'(\d{1,2})' + date_components_sep + r'(\d{' + str(year_digits_count) + r'})\b'
        elif date_component_order == 'mdy':
            return r'\b(\d{1,2})' + date_components_sep + r'(\d{1,2})' + date_components_sep + r'(\d{' + str(year_digits_count) + r'})\b'
        else:
            raise ValueError(f'Invalid date_component_order: {date_component_order}')

    def __str__(self):
        return f'{self.__class__.__name__}({self._pattern})'

    def _parse_from_pattern_match(self, match: Match[str], year_group: int, month_group: int, day_group: int, abbrev_year_prefix: str = '20') -> date:
        year = int(match.group(year_group))
        month = int(match.group(month_group))
        day = int(match.group(day_group))

        if self._abbrev_year and year < 100:
            year = int(abbrev_year_prefix + str(year))

        return date(year, month, day)

    def _parse_dates_and_substitute_projection(self, text: str, project: Callable[[date], str], capture_groups_start_at: int = 1, abbrev_year_prefix: str = '20') -> str:
        if self._date_component_order == YearMonthDayDigitsComponentOrder.YMD:
            year_group = capture_groups_start_at
            month_group = year_group + 1
            day_group = month_group + 1
        elif self._date_component_order == YearMonthDayDigitsComponentOrder.MDY:
            month_group = capture_groups_start_at
            day_group = month_group + 1
            year_group = day_group + 1
        elif self._date_component_order == YearMonthDayDigitsComponentOrder.DMY:
            day_group = capture_groups_start_at
            month_group = day_group + 1
            year_group = month_group + 1
        else:
            raise ValueError(f'Invalid date_component_order: {self._date_component_order}')

        date_parser_kwargs = dict(year_group=year_group, month_group=month_group, day_group=day_group, abbrev_year_prefix=abbrev_year_prefix)
        date_from_pattern_match: Callable[[Match[str]], date]
        date_from_pattern_match = functools.partial(self._parse_from_pattern_match, **date_parser_kwargs)

        def replace_match(match: Match[str]) -> str:
            return project(date_from_pattern_match(match=match))

        return re.sub(self._pattern, replace_match, text)

    def _parse_and_reformat_all(
        self,
        text: str,
        new_date_components_sep: str = '-',
        new_date_component_order: YearMonthDayDigitsComponentOrder = YearMonthDayDigitsComponentOrder.YMD,
        capture_groups_start_at: int = 1,
        abbrev_year_prefix: str = '20'
    ) -> str:
        if new_date_component_order == YearMonthDayDigitsComponentOrder.YMD:
            strftime_format = f'%Y{new_date_components_sep}%m{new_date_components_sep}%d'
        elif new_date_component_order == YearMonthDayDigitsComponentOrder.MDY:
            strftime_format = f'%m{new_date_components_sep}%d{new_date_components_sep}%Y'
        elif new_date_component_order == YearMonthDayDigitsComponentOrder.DMY:
            strftime_format = f'%d{new_date_components_sep}%m{new_date_components_sep}%Y'
        else:
            raise ValueError(f'Invalid date_component_order: {new_date_component_order}')

        def project(value: date) -> str:
            return value.strftime(strftime_format)

        return self._parse_dates_and_substitute_projection(text, project, capture_groups_start_at, abbrev_year_prefix)

    def create_substitutor(self,
                           new_date_components_sep: str = '-',
                           new_date_component_order: YearMonthDayDigitsComponentOrder = YearMonthDayDigitsComponentOrder.YMD,
                           abbrev_year_prefix: str = '20'
                           ) -> LabeledTextFunc:
        text_func = functools.partial(self._parse_and_reformat_all, new_date_components_sep=new_date_components_sep, new_date_component_order=new_date_component_order, abbrev_year_prefix=abbrev_year_prefix)
        return LabeledTextFunc(
            f'DateDigitsSubstitutionFactory._parse_and_reformat_all(date_components_sep: "{self._date_components_sep}"->"{new_date_components_sep}", date_component_order: "{self._date_component_order}"->"{new_date_component_order}", abbrev_year: {self._abbrev_year})',
            text_func
        )
