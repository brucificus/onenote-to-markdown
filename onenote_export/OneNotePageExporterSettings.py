import dataclasses

from collections.abc import Sequence
from typing import Dict, Literal, Union

import panflute

from markdown_dom.type_variables import PanfluteElementContainerElementCtor, PanfluteElementStyleValuePredicate, \
    PanfluteElementAttributeValuePredicate

OneNotePageContentStyleExportElementStyleRemovals = Dict[str, PanfluteElementStyleValuePredicate]
OneNotePageContentStyleExportElementStyleElementPushes = Dict[str, Dict[str, PanfluteElementContainerElementCtor]]

OneNotePageContentStyleExportElementClassRemovals = Sequence[str]
OneNotePageContentStyleExportElementClassElementPushes = Dict[str, PanfluteElementContainerElementCtor]

OneNotePageContentStyleExportElementDataStyleRemovals = Dict[str, PanfluteElementAttributeValuePredicate]


@dataclasses.dataclass
class OneNotePageContentExportElementStyleSettings:
    removals: OneNotePageContentStyleExportElementStyleRemovals
    pushes: OneNotePageContentStyleExportElementStyleElementPushes


@dataclasses.dataclass
class OneNotePageContentExportElementExtraAttributesSettings:
    removals: OneNotePageContentStyleExportElementDataStyleRemovals


@dataclasses.dataclass
class OneNotePageContentExportElementClassSettings:
    removals: OneNotePageContentStyleExportElementClassRemovals
    pushes: OneNotePageContentStyleExportElementClassElementPushes


@dataclasses.dataclass
class OneNotePageContentExportStyleSettings:
    all_elements: OneNotePageContentExportElementStyleSettings
    divs: OneNotePageContentExportElementStyleSettings
    all_table_elements: OneNotePageContentExportElementStyleSettings
    gridlike_table_elements: OneNotePageContentExportElementStyleSettings


@dataclasses.dataclass
class OneNotePageContentExportClassSettings:
    all_elements: OneNotePageContentExportElementClassSettings
    divs: OneNotePageContentExportElementClassSettings
    all_table_elements: OneNotePageContentExportElementClassSettings
    gridlike_table_elements: OneNotePageContentExportElementClassSettings


@dataclasses.dataclass
class OneNotePageContentExportExtraAttributesSettings:
    all_elements: OneNotePageContentExportElementExtraAttributesSettings


def create_background_color_style_pusher() -> PanfluteElementContainerElementCtor:
    def create_element(*args: panflute.Element) -> panflute.Element:
        orig_parent_style = args[0].parent.attributes['style']
        orig_parent_style_parsed = parse_html_style_attribute(orig_parent_style)
        background_color = orig_parent_style_parsed.get('background-color', None)

        new_element = panflute.Plain(*args)
        new_element.attributes['style'] = f'background-color: {background_color};'
        return new_element

    return create_element


@dataclasses.dataclass
class OneNotePageExporterSettings:
    pages_remove_onenote_footer: bool
    pages_extra_attributes_settings: OneNotePageContentExportExtraAttributesSettings
    pages_content_style_settings: OneNotePageContentExportStyleSettings
    pages_content_class_settings: OneNotePageContentExportClassSettings
    pages_table_element_colspec_handling: Union[None, Literal['remove_all_width_specifiers']] = 'reset_all_width_specifiers'

    @classmethod
    def create_default(cls):
        return cls(
            pages_remove_onenote_footer=True,
            pages_extra_attributes_settings=OneNotePageContentExportExtraAttributesSettings(
                all_elements=OneNotePageContentExportElementExtraAttributesSettings(
                    removals={
                        'valign': lambda v: v == 'top',
                        'border': lambda _: True,
                        'cellpadding': lambda _: True,
                        'cellspacing': lambda _: True,
                        'title': lambda v: (not v) or (v.strip() == ''),
                        'summary': lambda v: (not v) or (v.strip() == ''),
                        'data-valign': lambda v: v == 'top',
                        'data-border': lambda _: True,
                        'data-cellpadding': lambda _: True,
                        'data-cellspacing': lambda _: True,
                        'data-title': lambda v: (not v) or (v.strip() == ''),
                        'data-summary': lambda v: (not v) or (v.strip() == ''),
                    }
                ),
            ),
            pages_content_style_settings=OneNotePageContentExportStyleSettings(
                all_elements=OneNotePageContentExportElementStyleSettings(
                    removals={
                        'direction': ('ltr',),
                        'font-family': ('Calibri', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Segoe UI Light', 'inherit'),
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
                ),
                all_table_elements=OneNotePageContentExportElementStyleSettings(
                    removals={
                        'border-color': lambda v: True,
                        'border-style': lambda v: v == 'solid',
                        'border-width': lambda v: True,
                        'vertical-align': lambda v: v == 'top',
                        'border-collapse': lambda v: v == 'collapse',
                        'font-size': lambda v, u: (abs(v - 1.0) < 0.01) and u == 'pt',
                    },
                    pushes={},
                ),
                gridlike_table_elements=OneNotePageContentExportElementStyleSettings(
                    removals={
                        'width': lambda v: True,
                        'height': lambda v: True,
                        'padding': lambda v: True,
                        'margin': lambda v: True,
                        'margin-top': lambda v: True,
                        'margin-left': lambda v: True,
                        'margin-right': lambda v: True,
                        'margin-bottom': lambda v: True,
                        'padding-top': lambda v: True,
                        'padding-left': lambda v: True,
                        'padding-right': lambda v: True,
                        'padding-bottom': lambda v: True,

                    },
                    pushes={},
                ),
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
                    pushes={
                        'background-color': create_background_color_style_pusher(),
                    },
                ),
                all_table_elements=OneNotePageContentExportElementClassSettings(
                    removals=(),
                    pushes={},
                ),
                gridlike_table_elements=OneNotePageContentExportElementClassSettings(
                    removals=(
                        'even',
                        'odd',
                    ),
                    pushes={},
                ),
            ),
        )
