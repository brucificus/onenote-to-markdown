import functools
import re
from datetime import time
from typing import Pattern, Optional, Match, Callable

from .LabeledTextFunc import LabeledTextFunc


class TimeDigitsSubstitutionFactory:
    def __init__(self, time_components_sep: str = ':', expect_seconds: bool = True, twelve_hour: bool = True):
        self._time_components_sep = time_components_sep
        self._expect_seconds = expect_seconds
        self._twelve_hour = twelve_hour
        self._pattern = self._create_regex_pattern(time_components_sep, expect_seconds, twelve_hour)

    def _create_regex_pattern(self, time_components_sep: str = ':', expect_seconds: bool = True, twelve_hour: bool = True) -> Pattern[str]:
        if expect_seconds:
            if twelve_hour:
                return re.compile(r'\b(\d{1,2})' + time_components_sep + r'(\d{2})' + time_components_sep + r'(\d{2})\s+(AM|PM)', re.IGNORECASE)
            else:
                return re.compile(r'\b(\d{1,2})' + time_components_sep + r'(\d{2})' + time_components_sep + r'(\d{2})')
        else:
            if twelve_hour:
                return re.compile(r'\b(\d{1,2})' + time_components_sep + r'(\d{2})\s+(AM|PM)', re.IGNORECASE)
            else:
                return re.compile(r'\b(\d{1,2})' + time_components_sep + r'(\d{2})')

    def __str__(self):
        return f'TimeSubstitutionFactory({self._time_components_sep}, {self._expect_seconds}, {self._twelve_hour})'

    def _parse_12hr_time_from_pattern_match(self, match: Match[str], hour_group: int, minute_group: int, second_group: Optional[int], am_pm_group: int) -> time:
        hour = int(match.group(hour_group))
        minute = int(match.group(minute_group))
        second = int(match.group(second_group)) if second_group is not None else 0
        am_pm = match.group(am_pm_group).lower()
        if am_pm == 'pm':
            hour += 12
        if hour == 24:
            hour = 0
        return time(hour, minute, second)

    def _parse_24hr_time_from_pattern_match(self, match: Match[str], hour_group: int, minute_group: int, second_group: Optional[int]) -> time:
        hour = int(match.group(hour_group))
        minute = int(match.group(minute_group))
        second = int(match.group(second_group)) if second_group is not None else 0
        return time(hour, minute, second)

    def _parse_times_and_substitute_projection(self, text: str, project: Callable[[time], str], capture_groups_start_at: int = 1) -> str:
        hour_group = capture_groups_start_at
        minute_group = hour_group + 1
        second_group = minute_group + 1 if self._expect_seconds else None
        time_parser_kwargs = dict(hour_group=hour_group, minute_group=minute_group, second_group=second_group)
        time_parser: Callable[[Match[str]], time]
        if self._twelve_hour:
            am_pm_group = second_group + 1 if self._expect_seconds else minute_group + 1
            time_parser_kwargs['am_pm_group'] = am_pm_group
            time_parser = self._parse_12hr_time_from_pattern_match
        else:
            time_parser = self._parse_24hr_time_from_pattern_match

        time_from_pattern_match = functools.partial(time_parser, **time_parser_kwargs)

        def replace_match(match: Match[str]) -> str:
            return project(time_from_pattern_match(match=match))

        return re.sub(self._pattern, replace_match, text)

    def _parse_and_reformat_all(self, text: str, new_time_components_sep: str, include_missing_seconds: bool = False, capture_groups_start_at: int = 1, coerce_to_24hr_iso8601: bool = False) -> str:
        output_seconds = self._expect_seconds or include_missing_seconds

        if self._twelve_hour and not coerce_to_24hr_iso8601:
            if output_seconds:
                strftime_format = f'%I{new_time_components_sep}%M{new_time_components_sep}%S %p'
            else:
                strftime_format = f'%I{new_time_components_sep}%M %p'
        else:
            if output_seconds:
                strftime_format = f'%H{new_time_components_sep}%M{new_time_components_sep}%S'
            else:
                strftime_format = f'%H{new_time_components_sep}%M'

        def project(value: time) -> str:
            return value.strftime(strftime_format)

        return self._parse_times_and_substitute_projection(text, project, capture_groups_start_at)

    def _coerce_to_24hr_iso8601(self, text: str, include_missing_seconds: bool = False, capture_groups_start_at: int = 1) -> str:
        return self._parse_and_reformat_all(text, new_time_components_sep=':', include_missing_seconds=include_missing_seconds, capture_groups_start_at=capture_groups_start_at, coerce_to_24hr_iso8601=True)

    def create_substitutor_replacing_separator(self, new_time_components_sep: str, include_missing_seconds: bool = False, capture_groups_start_at: int = 1) -> LabeledTextFunc:
        text_func = functools.partial(self._parse_and_reformat_all, new_time_components_sep=new_time_components_sep, include_missing_seconds=include_missing_seconds, capture_groups_start_at=capture_groups_start_at)
        return LabeledTextFunc(
            f'TimeDigitsSubstitutionFactory._parse_and_reformat_all(time_components_sep: "{self._time_components_sep}"->"{new_time_components_sep}", expect_seconds: {self._expect_seconds}, twelve_hour: {self._twelve_hour}, include_missing_seconds: {include_missing_seconds})',
            text_func
        )

    def create_substitutor_coercing_to_24hr_iso8601(self, include_missing_seconds: bool = False, capture_groups_start_at: int = 1) -> LabeledTextFunc:
        text_func = functools.partial(self._coerce_to_24hr_iso8601, include_missing_seconds=include_missing_seconds, capture_groups_start_at=capture_groups_start_at)
        return LabeledTextFunc(
            f'TimeDigitsSubstitutionFactory._coerce_to_24hr_iso8601(expect_seconds: {self._expect_seconds}, twelve_hour: {self._twelve_hour}, include_missing_seconds: {include_missing_seconds})',
            text_func
        )
