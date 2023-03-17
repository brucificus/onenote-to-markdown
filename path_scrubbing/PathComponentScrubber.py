import functools
import pathlib
from functools import reduce, cache
from typing import Callable, Iterable, Optional, Tuple

from .AbbrevYearPrefix import AbbrevYearPrefix
from .LabeledRegexSubstitution import LabeledRegexSubstitution
from .DateDigitsSubstitutionFactory import DateDigitsSubstitutionFactory
from .TimeDigitsSubstitutionFactory import TimeDigitsSubstitutionFactory
from .os_paths_support import os_paths_support_character


class PathComponentScrubber:
    def __init__(self):
        self._prefer_zettelkasten_style_timestamp_infixes: bool = True
        self._abbrev_year_prefix: Optional[AbbrevYearPrefix] = AbbrevYearPrefix.TWENTY
        self._reformat_datetimes_separated_by: Tuple[str, ...] = ('_',)
        self._reformat_times_fill_empty_seconds: bool = False
        self._reformat_all_times_coercing_to_24hr_iso8601: bool = True

    def _yield_path_cleanup_substitutions(self) -> Iterable[Callable[[str], str]]:
        os_paths_support_slashes = os_paths_support_character('/')
        os_paths_support_colons = os_paths_support_character(':')
        os_paths_support_lessthan = os_paths_support_character('<')
        os_paths_support_greaterthan = os_paths_support_character('>')
        os_paths_support_pipes = os_paths_support_character('|')
        os_paths_support_question = os_paths_support_character('?')
        os_paths_support_fullwidthasterisks = os_paths_support_character('＊')
        os_paths_support_division_solidi = os_paths_support_character('∕')
        os_paths_support_emdashes = os_paths_support_character('—')
        os_paths_support_endashes = os_paths_support_character('–')
        os_paths_support_highcolons = os_paths_support_character('˸')
        os_paths_support_smartdoublequotes = os_paths_support_character('“') and os_paths_support_character('”')
        os_paths_support_fullwidthlessthan = os_paths_support_character('＜')
        os_paths_support_fullwidthgreaterthan = os_paths_support_character('＞')
        os_paths_support_fullwidthverticalline = os_paths_support_character('｜')
        os_paths_support_fullwidthquestion = os_paths_support_character('？')

        def _yield_path_cleanup_substitutions_for_dates_times_and_datetimes() -> Iterable[Callable[[str], str]]:
            slashed_mdy_dates_pattern = functools.partial(DateDigitsSubstitutionFactory, '/', date_component_order='mdy')
            slashed_ymd_dates_pattern = functools.partial(DateDigitsSubstitutionFactory, '/', date_component_order='ymd')

            dates_replacement_seperator = '/' if os_paths_support_slashes or self._prefer_zettelkasten_style_timestamp_infixes else '-'
            times_replacement_separator = ':' if os_paths_support_colons or self._prefer_zettelkasten_style_timestamp_infixes else '_'
            for separator in self._reformat_datetimes_separated_by:
                separator_separated_mdy_dates_pattern = functools.partial(DateDigitsSubstitutionFactory, separator, date_component_order='mdy')
                separator_separated_ymd_dates_pattern = functools.partial(DateDigitsSubstitutionFactory, separator, date_component_order='ymd')
                yield separator_separated_mdy_dates_pattern(abbrev_year=False).create_substitutor(new_date_components_sep=dates_replacement_seperator)
                if self._abbrev_year_prefix is not None:
                    yield separator_separated_mdy_dates_pattern(abbrev_year=True).create_substitutor(new_date_components_sep=dates_replacement_seperator, abbrev_year_prefix=self._abbrev_year_prefix)
                yield separator_separated_ymd_dates_pattern(abbrev_year=False).create_substitutor(new_date_components_sep=dates_replacement_seperator)
                if self._abbrev_year_prefix is not None:
                    yield separator_separated_ymd_dates_pattern(abbrev_year=True).create_substitutor(new_date_components_sep=dates_replacement_seperator, abbrev_year_prefix=self._abbrev_year_prefix)
                yield LabeledRegexSubstitution(f'Year-Month Date MM{separator}YYYY to YYYY{dates_replacement_seperator}MM', r'\b(\d{1,2})' + separator + r'(\d{4})\b', r'\2' + dates_replacement_seperator + '\1')

                yield TimeDigitsSubstitutionFactory(time_components_sep=separator, expect_seconds=True, twelve_hour=True).create_substitutor_replacing_separator(new_time_components_sep=times_replacement_separator)
                yield TimeDigitsSubstitutionFactory(time_components_sep=separator, expect_seconds=True, twelve_hour=False).create_substitutor_replacing_separator(new_time_components_sep=times_replacement_separator)
                yield TimeDigitsSubstitutionFactory(time_components_sep=separator, expect_seconds=False, twelve_hour=True).create_substitutor_replacing_separator(new_time_components_sep=times_replacement_separator, include_missing_seconds=self._reformat_times_fill_empty_seconds)
                yield TimeDigitsSubstitutionFactory(time_components_sep=separator, expect_seconds=False, twelve_hour=False).create_substitutor_replacing_separator(new_time_components_sep=times_replacement_separator, include_missing_seconds=self._reformat_times_fill_empty_seconds)

            if not os_paths_support_slashes:
                yield slashed_mdy_dates_pattern(abbrev_year=False).create_substitutor()
                if self._abbrev_year_prefix is not None:
                    yield slashed_mdy_dates_pattern(abbrev_year=True).create_substitutor(abbrev_year_prefix=self._abbrev_year_prefix)
                yield slashed_ymd_dates_pattern(abbrev_year=False).create_substitutor()
                if self._abbrev_year_prefix is not None:
                    yield slashed_ymd_dates_pattern(abbrev_year=True).create_substitutor(abbrev_year_prefix=self._abbrev_year_prefix)
                yield LabeledRegexSubstitution(f'Year-Month Date MM/YYYY to YYYY-MM', r'\b(\d{1,2})/(\d{4})\b', r'\2-\1')

            # TODO: Add support for 'Mmm DD, YYYY' and 'Mmm DD YYYY' formats.
            #       Convert them to ISO 8601 format as needed, convert them to zettelkasten-style as needed.

            if not os_paths_support_colons:
                yield TimeDigitsSubstitutionFactory(time_components_sep=':', expect_seconds=True, twelve_hour=True).create_substitutor_replacing_separator(new_time_components_sep=times_replacement_separator)
                yield TimeDigitsSubstitutionFactory(time_components_sep=':', expect_seconds=True, twelve_hour=False).create_substitutor_replacing_separator(new_time_components_sep=times_replacement_separator)
                yield TimeDigitsSubstitutionFactory(time_components_sep=':', expect_seconds=False, twelve_hour=True).create_substitutor_replacing_separator(new_time_components_sep=times_replacement_separator, include_missing_seconds=self._reformat_times_fill_empty_seconds)
                yield TimeDigitsSubstitutionFactory(time_components_sep=':', expect_seconds=False, twelve_hour=False).create_substitutor_replacing_separator(new_time_components_sep=times_replacement_separator, include_missing_seconds=self._reformat_times_fill_empty_seconds)

            if self._reformat_all_times_coercing_to_24hr_iso8601 or self._prefer_zettelkasten_style_timestamp_infixes:
                # If 'prefer_zettelkasten_style_timestamp_infixes', we need to coerce all times to 24hr ISO 8601 format _first_.
                yield TimeDigitsSubstitutionFactory(time_components_sep=times_replacement_separator, expect_seconds=True, twelve_hour=True).create_substitutor_coercing_to_24hr_iso8601()
                yield TimeDigitsSubstitutionFactory(time_components_sep=times_replacement_separator, expect_seconds=True, twelve_hour=False).create_substitutor_coercing_to_24hr_iso8601()
                yield TimeDigitsSubstitutionFactory(time_components_sep=times_replacement_separator, expect_seconds=False, twelve_hour=True).create_substitutor_coercing_to_24hr_iso8601(include_missing_seconds=self._reformat_times_fill_empty_seconds)
                yield TimeDigitsSubstitutionFactory(time_components_sep=times_replacement_separator, expect_seconds=False, twelve_hour=False).create_substitutor_coercing_to_24hr_iso8601(include_missing_seconds=self._reformat_times_fill_empty_seconds)

            if self._prefer_zettelkasten_style_timestamp_infixes:
                yield LabeledRegexSubstitution('ISO 8601 Full DateTime (w/ Seconds) to Zettelkasten', r'\b(\d{4})-(\d{2})-(\d{2})(T|\s+)(\d{1,2}):(\d{2}):(\d{2})\b', r'\1\2\3\5\6\7')
                if self._reformat_times_fill_empty_seconds:
                    yield LabeledRegexSubstitution('ISO 8601 Full DateTime (w/o Seconds) to Zettelkasten', r'\b(\d{4})-(\d{2})-(\d{2})(T|\s+)(\d{1,2}):(\d{2})\b', r'\1\2\3\5\g<6>00')
                else:
                    yield LabeledRegexSubstitution('ISO 8601 Full DateTime (w/o Seconds) to Zettelkasten', r'\b(\d{4})-(\d{2})-(\d{2})(T|\s+)(\d{1,2}):(\d{2})\b', r'\1\2\3\5\6')

                if times_replacement_separator != ':':
                    yield TimeDigitsSubstitutionFactory(time_components_sep=times_replacement_separator, expect_seconds=True, twelve_hour=False).create_substitutor_replacing_separator(new_time_components_sep='')
                    yield TimeDigitsSubstitutionFactory(time_components_sep=times_replacement_separator, expect_seconds=False, twelve_hour=False).create_substitutor_replacing_separator(new_time_components_sep='', include_missing_seconds=self._reformat_times_fill_empty_seconds)
                yield TimeDigitsSubstitutionFactory(time_components_sep=':', expect_seconds=True, twelve_hour=False).create_substitutor_replacing_separator(new_time_components_sep='')
                yield TimeDigitsSubstitutionFactory(time_components_sep=':', expect_seconds=False, twelve_hour=False).create_substitutor_replacing_separator(new_time_components_sep='', include_missing_seconds=self._reformat_times_fill_empty_seconds)

        for substitution in _yield_path_cleanup_substitutions_for_dates_times_and_datetimes():
            yield substitution

        if not os_paths_support_colons:
            if os_paths_support_emdashes:
                yield LabeledRegexSubstitution('Word-Colon-Space to Emdash', r'(\w):(\s+)', r'\1 —\2')
            if os_paths_support_highcolons:
                yield LabeledRegexSubstitution('Colon to HighColon', r':', r'˸')
        if os_paths_support_smartdoublequotes:
            yield LabeledRegexSubstitution('Decimal-DoubleQuote to Smart DoubleQuote', r'(\d+)"', r'\1”')
            yield LabeledRegexSubstitution('DoubleQuote Pairs to Smart DoubleQuotes', r'(")([^"]*)(")', r'“\2”')
        if os_paths_support_fullwidthasterisks:
            yield LabeledRegexSubstitution('Asterisk to HeavyAsterisk', r'\*', r'＊')
        if os_paths_support_division_solidi and not os_paths_support_slashes:
            yield LabeledRegexSubstitution('Slash to Solidus', r'/', r'∕')
        if not os_paths_support_emdashes:
            yield LabeledRegexSubstitution('Emdash to Hyphen', r'—', r'-')
        if not os_paths_support_endashes:
            yield LabeledRegexSubstitution('Endash to Hyphen', r'–', r'-')
        if not os_paths_support_lessthan and os_paths_support_fullwidthlessthan:
            yield LabeledRegexSubstitution('LessThan to FullwidthLessThan', r'<', r'＜')
        if not os_paths_support_greaterthan and os_paths_support_fullwidthgreaterthan:
            yield LabeledRegexSubstitution('GreaterThan to FullwidthGreaterThan', r'>', r'＞')
        if not os_paths_support_pipes and os_paths_support_fullwidthverticalline:
            yield LabeledRegexSubstitution('Pipe to FullwidthVerticalline', r'\|', r'｜')
        if not os_paths_support_question and os_paths_support_fullwidthquestion:
            yield LabeledRegexSubstitution('Question to FullwidthQuestion', r'\?', r'？')

    @property
    @cache
    def _path_cleanup_substitutions(self) -> Tuple[Callable[[str], str], ...]:
        return tuple(self._yield_path_cleanup_substitutions())

    def cleanup_path_component(self, path: str) -> pathlib.Path:
        cleaned_path_text = reduce(
            lambda updated_path_text, substitution: substitution(updated_path_text),
            self._path_cleanup_substitutions,
            path)
        return pathlib.Path(cleaned_path_text)
