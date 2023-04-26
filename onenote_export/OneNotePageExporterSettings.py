import dataclasses

from collections.abc import Sequence
from typing import Dict

import panflute

from markdown_dom.type_variables import PanfluteElementContainerElementCtor, PanfluteElementStyleValuePredicate

OneNotePageContentStyleExportElementStyleRemovals = Dict[str, PanfluteElementStyleValuePredicate]
OneNotePageContentStyleExportElementStyleElementPushes = Dict[str, Dict[str, PanfluteElementContainerElementCtor]]

OneNotePageContentStyleExportElementClassRemovals = Sequence[str]
OneNotePageContentStyleExportElementClassElementPushes = Dict[str, PanfluteElementContainerElementCtor]


@dataclasses.dataclass
class OneNotePageContentExportElementStyleSettings:
    removals: OneNotePageContentStyleExportElementStyleRemovals
    pushes: OneNotePageContentStyleExportElementStyleElementPushes


@dataclasses.dataclass
class OneNotePageContentExportElementClassSettings:
    removals: OneNotePageContentStyleExportElementClassRemovals
    pushes: OneNotePageContentStyleExportElementClassElementPushes


@dataclasses.dataclass
class OneNotePageContentExportStyleSettings:
    all_elements: OneNotePageContentExportElementStyleSettings
    divs: OneNotePageContentExportElementStyleSettings


@dataclasses.dataclass
class OneNotePageContentExportClassSettings:
    all_elements: OneNotePageContentExportElementClassSettings
    divs: OneNotePageContentExportElementClassSettings


@dataclasses.dataclass
class OneNotePageExporterSettings:
    pages_remove_onenote_footer: bool
    pages_content_style_settings: OneNotePageContentExportStyleSettings
    pages_content_class_settings: OneNotePageContentExportClassSettings

    @classmethod
    def create_default(cls):
        return cls(
            pages_remove_onenote_footer=True,
            pages_content_style_settings=OneNotePageContentExportStyleSettings(
                all_elements=OneNotePageContentExportElementStyleSettings(
                    removals={
                        'direction': ('ltr',),
                        'font-family': ('Calibri', 'Segoe UI Emoji', 'inherit'),
                        'font-size': ('11.0pt',),
                        'font-weight': ('normal',),
                        'font-style': ('normal',),
                        'mso-spacerun': ('yes',),
                    },
                    pushes={
                        'text-decoration': {
                            'underline': panflute.Underline,
                            'line-through': panflute.Strikeout,
                        },
                        'font-weight': {
                            'bold': panflute.Strong,
                        },
                        'font-style': {
                            'italic': panflute.Emph,
                        },
                    },
                ),
                divs=OneNotePageContentExportElementStyleSettings(
                    removals={
                        'margin-top': lambda v: True,
                        'margin-left': lambda v: True,
                        'width': lambda v: True,
                        'border-width': lambda v: True,
                    },
                    pushes={},
                )
            ),
            pages_content_class_settings=OneNotePageContentExportClassSettings(
                all_elements=OneNotePageContentExportElementClassSettings(
                    removals=(),
                    pushes={
                        'underline': panflute.Underline,
                    },
                ),
                divs=OneNotePageContentExportElementClassSettings(
                    removals=(),
                    pushes={},
                ),
            ),
        )
