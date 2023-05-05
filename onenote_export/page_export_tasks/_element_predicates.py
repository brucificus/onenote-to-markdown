from typing import Optional

import panflute

from markdown_dom.PanfluteElementAccumulatorElementFilterContext import PanfluteElementAccumulatorElementFilterContext
from markdown_dom.type_variables import PanfluteElementAttributeValuePredicate, PanfluteElementStyleValuePredicate
from onenote_export.page_export_tasks._element_attribute_predicates import attribute_value_is_match, style_has_match
from onenote_export.page_export_tasks._style_attribute import parse_html_style_attribute


promotion_combinable_element_transitions = (
    (panflute.Div, panflute.Doc),
    (panflute.Span, panflute.Doc),

    (panflute.Div, panflute.Div),
    (panflute.Span, panflute.Span),
    (panflute.Strikeout, panflute.Strikeout),
    (panflute.Strong, panflute.Strong),
    (panflute.Underline, panflute.Underline),
    (panflute.Emph, panflute.Emph),
    (panflute.Subscript, panflute.Subscript),
    (panflute.Superscript, panflute.Superscript),
    (panflute.Plain, panflute.Plain),
    (panflute.Para, panflute.Para),

    (panflute.Span, panflute.Plain),
    (panflute.Span, panflute.Div),
    (panflute.Span, panflute.ListItem),
    (panflute.Span, panflute.Strikeout),
    (panflute.Span, panflute.Strong),
    (panflute.Span, panflute.Underline),
    (panflute.Span, panflute.Emph),
    (panflute.Span, panflute.Subscript),
    (panflute.Span, panflute.Superscript),

    (panflute.Span, panflute.Link),

    (panflute.Span, panflute.Image),
    (panflute.Div, panflute.Image),

    (panflute.Span, panflute.Para),
    (panflute.Plain, panflute.Para),
)


def element_is_table_element(element: panflute.Element) -> bool:
    return isinstance(element, (panflute.Table, panflute.TableCell, panflute.TableRow, panflute.TableFoot, panflute.TableHead, panflute.TableBody))


def element_has_nongridlike_nested_elements(table: panflute.Table) -> bool:
    return PanfluteElementAccumulatorElementFilterContext.any_elements(table, lambda e: element_is_table_element(e) and ('rowspan' in e.attributes or 'colspan' in e.attributes))


def element_has_styled_table_elements(table: panflute.Table) -> bool:
    return PanfluteElementAccumulatorElementFilterContext.any_elements(table, lambda e: element_is_table_element(e) and (('style' in e.attributes and e.attributes['style']) or e.classes))


def element_is_gridlike_table(table: panflute.Table) -> bool:
    return isinstance(table, panflute.Table) and not element_has_nongridlike_nested_elements(table)


def element_is_in_gridlike_table(element: panflute.Element) -> bool:
    return element_is_gridlike_table(get_element_parent_table(element))


def element_is_div_element(element: panflute.Element) -> bool:
    return isinstance(element, panflute.Div)


def element_is_table_element_in_gridlike_table(element: panflute.Element) -> bool:
    return element_is_table_element(element) and (element_is_gridlike_table(element) or element_is_in_gridlike_table(element))


def element_is_table_element_in_table(element: panflute.Element) -> bool:
    return element_is_table_element(element) and (isinstance(element, panflute.Table) or get_element_parent_table(element))


def element_has_attributes(element: panflute.Element) -> bool:
    return isinstance(element, panflute.Element) and hasattr(element, "attributes") and element.attributes


def element_has_attribute(element: panflute.Element, attribute_name: str) -> bool:
    return element_has_attributes(element) and attribute_name in element.attributes


def element_has_style(element: panflute.Element) -> bool:
    return element_has_attribute(element, "style") and element.attributes["style"] != ''


def element_has_specific_style_value(element: panflute.Element, style_name: str, style_value_condition: Optional[PanfluteElementStyleValuePredicate]) -> bool:
    if not element_has_style(element):
        return False
    style_parsed = parse_html_style_attribute(element.attributes["style"])
    return style_has_match(style_parsed, style_name, style_value_condition)


def element_has_classes(element: panflute.Element) -> bool:
    return isinstance(element, panflute.Element) and hasattr(element, "classes") and element.classes


def element_has_specific_class(element: panflute.Element, class_name: str) -> bool:
    return element_has_classes(element) and class_name in element.classes


def element_is_div_with_any_style(element: panflute.Element) -> bool:
    return element_has_style(element) and element_is_div_element(element)


def element_is_div_with_any_classes(element: panflute.Element) -> bool:
    return element_has_classes(element) and element_is_div_element(element)


def get_element_parent_table(element: panflute.Element) -> Optional[panflute.Table]:
    parent = element.parent
    while parent is not None and not isinstance(parent, panflute.Table):
        parent = parent.parent
    return parent


def element_is_valid_for_children_promotion(element: panflute.Element) -> bool:
    classes_empty = (not hasattr(element, "classes") or (hasattr(element, "classes") and not element.classes))
    attributes_empty = (not hasattr(element, "attributes") or (hasattr(element, "attributes") and not element.attributes))

    element_type_pairs_valid = any(
        isinstance(element, possible_combo[0]) and isinstance(element.parent, possible_combo[1])
        for possible_combo in promotion_combinable_element_transitions
    )
    return classes_empty and attributes_empty and element_type_pairs_valid


def element_has_data_attributes(element: panflute.Element) -> bool:
    return isinstance(element, panflute.Element) \
        and hasattr(element, "attributes") \
        and any(attribute_name.startswith("data-") for attribute_name in element.attributes)


def element_has_data_attribute_value(element, data_attribute_name_suffix: str, data_attribute_value_condition: PanfluteElementAttributeValuePredicate):
    if not element_has_data_attributes(element):
        return False

    data_attribute_name = f"data-{data_attribute_name_suffix}"
    if data_attribute_name not in element.attributes:
        return False
    data_attribute_value = element.attributes[data_attribute_name]
    return attribute_value_is_match(data_attribute_value, data_attribute_value_condition)
