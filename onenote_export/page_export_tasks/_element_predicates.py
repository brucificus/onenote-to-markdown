from typing import Optional

import panflute

from markdown_dom.PanfluteElementAccumulatorElementFilterContext import PanfluteElementAccumulatorElementFilterContext
from markdown_dom.type_variables import PanfluteElementAttributeValuePredicate, PanfluteElementStyleValuePredicate, \
    PanfluteElementPredicate
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


class PanfluteElementPredicateDescription:
    def __init__(self, description):
        self._description = description

    def __call__(self, func):
        func.description = self._description
        return func

    @staticmethod
    def read_from(element_predicate: PanfluteElementPredicate) -> 'str':
        if hasattr(element_predicate, "description"):
            return element_predicate.description
        if hasattr(element_predicate, "__name__"):
            return element_predicate.__name__
        return str(element_predicate)


@PanfluteElementPredicateDescription("element is a table element")
def element_is_table_element(element: panflute.Element) -> bool:
    return isinstance(element, (panflute.Table, panflute.TableCell, panflute.TableRow, panflute.TableFoot, panflute.TableHead, panflute.TableBody))


@PanfluteElementPredicateDescription("element is a table element which indirectly makes meaningful use of rowspan or colspan")
def element_has_nongridlike_nested_elements(table: panflute.Table) -> bool:
    def _table_element_has_meaningful_rowspan(element: panflute.Element) -> bool:
        return element_has_attribute(element, "rowspan") \
            and element.attributes["rowspan"].strip() != '' \
            and int(element.attributes["rowspan"]) > 1

    def _table_element_has_meaningful_colspan(element: panflute.Element) -> bool:
        return element_has_attribute(element, "colspan") \
            and element.attributes["colspan"].strip() != '' \
            and int(element.attributes["colspan"]) > 1

    def _table_element_has_meaningful_rowspan_or_colspan(element: panflute.Element) -> bool:
        return _table_element_has_meaningful_rowspan(element) or _table_element_has_meaningful_colspan(element)

    @PanfluteElementPredicateDescription("element is a table element which directly makes meaningful use of rowspan or colspan")
    def element_is_table_element_with_meaningful_rowspan_or_colspan(element: panflute.Element) -> bool:
        return element_is_table_element(element) and _table_element_has_meaningful_rowspan_or_colspan(element)

    return PanfluteElementAccumulatorElementFilterContext.any_elements(table, element_is_table_element_with_meaningful_rowspan_or_colspan)


@PanfluteElementPredicateDescription("element is a table element which indirectly includes any elements with meaningful style or class items")
def element_is_table_with_any_stylized_descendant_elements(table: panflute.Table) -> bool:
    @PanfluteElementPredicateDescription("element is a table element which indirectly includes any elements with meaningful style or class items")
    def element_is_table_element_with_style_or_class(element: panflute.Element) -> bool:
        return element_is_table_element(element) and (element_has_style(element) or element_has_classes(element))

    return PanfluteElementAccumulatorElementFilterContext.any_elements(table, element_is_table_element_with_style_or_class)


@PanfluteElementPredicateDescription("element is a gridlike table")
def element_is_gridlike_table(table: panflute.Table) -> bool:
    return isinstance(table, panflute.Table) and not element_has_nongridlike_nested_elements(table)


@PanfluteElementPredicateDescription("element is nested within a gridlike table")
def element_is_in_gridlike_table(element: panflute.Element) -> bool:
    return element_is_gridlike_table(get_element_table(element))


@PanfluteElementPredicateDescription("element is a Div")
def element_is_div_element(element: panflute.Element) -> bool:
    return isinstance(element, panflute.Div)


@PanfluteElementPredicateDescription("element is a table element nested within a gridlike table")
def element_is_table_element_in_gridlike_table(element: panflute.Element) -> bool:
    return element_is_table_element(element) and element_is_in_gridlike_table(element)


@PanfluteElementPredicateDescription("element is a table element nested within a table")
def element_is_table_element_in_table(element: panflute.Element) -> bool:
    return element_is_table_element(element) and (isinstance(element, panflute.Table) or get_element_table(element))


@PanfluteElementPredicateDescription("element has attributes")
def element_has_attributes(element: panflute.Element) -> bool:
    return hasattr(element, "attributes") and element.attributes


@PanfluteElementPredicateDescription("element has a specific attribute '{attribute_name}'")
def element_has_attribute(element: panflute.Element, attribute_name: str) -> bool:
    return element_has_attributes(element) and attribute_name in element.attributes


@PanfluteElementPredicateDescription("element has a meaningful style")
def element_has_style(element: panflute.Element) -> bool:
    return element_has_attribute(element, "style") and element.attributes["style"].strip() != ''


@PanfluteElementPredicateDescription("element has a specific style item '{attribute_name}' with a value satisfying '{style_value_condition}'")
def element_has_specific_style_value(element: panflute.Element, style_name: str, style_value_condition: Optional[PanfluteElementStyleValuePredicate]) -> bool:
    if not element_has_style(element):
        return False
    style_parsed = parse_html_style_attribute(element.attributes["style"])
    return style_has_match(style_parsed, style_name, style_value_condition)


@PanfluteElementPredicateDescription("element has meaningful classes")
def element_has_classes(element: panflute.Element) -> bool:
    return hasattr(element, "classes") and element.classes and len(element.classes) > 0


@PanfluteElementPredicateDescription("element has a specific class '{class_name}'")
def element_has_specific_class(element: panflute.Element, class_name: str) -> bool:
    return element_has_classes(element) and class_name in element.classes


@PanfluteElementPredicateDescription("element is div with meaningful style")
def element_is_div_with_any_style(element: panflute.Element) -> bool:
    return element_has_style(element) and element_is_div_element(element)


@PanfluteElementPredicateDescription("element is div with meaningful classes")
def element_is_div_with_any_classes(element: panflute.Element) -> bool:
    return element_has_classes(element) and element_is_div_element(element)


def get_element_table(element: panflute.Element) -> Optional[panflute.Table]:
    parent = element
    while parent is not None and not isinstance(parent, panflute.Table):
        parent = parent.parent
    return parent


@PanfluteElementPredicateDescription("element and its parent are a whitelisted combination for child element promotion")
def element_is_valid_for_children_promotion(element: panflute.Element) -> bool:
    classes_empty = (not hasattr(element, "classes") or (hasattr(element, "classes") and not element.classes))
    attributes_empty = (not hasattr(element, "attributes") or (hasattr(element, "attributes") and not element.attributes))

    element_type_pairs_valid = any(
        isinstance(element, possible_combo[0]) and isinstance(element.parent, possible_combo[1])
        for possible_combo in promotion_combinable_element_transitions
    )
    return classes_empty and attributes_empty and element_type_pairs_valid


@PanfluteElementPredicateDescription("element has a specific attribute '{attribute_name}' with a value satisfying '{attribute_value_condition}'")
def element_has_attribute_value(element, attribute_name: str, attribute_value_condition: PanfluteElementAttributeValuePredicate):
    if not element_has_attributes(element):
        return False

    if attribute_name not in element.attributes:
        return False
    attribute_value = element.attributes[attribute_name]
    return attribute_value_is_match(attribute_value, attribute_value_condition)
