import inspect
import re
from typing import Sequence, Iterable, Callable, Dict, Optional

from markdown_dom.type_variables import PanfluteElementAttributeValuePredicate, PanfluteElementStyleValuePredicate


def attribute_value_is_match(attribute_value: str, attribute_value_condition: PanfluteElementAttributeValuePredicate) -> bool:
    if attribute_value_condition is None:
        return True
    if isinstance(attribute_value_condition, bool):
        return attribute_value_condition
    if isinstance(attribute_value_condition, str):
        return attribute_value in (attribute_value_condition, f'"{attribute_value_condition}"')
    if isinstance(attribute_value_condition, Sequence):
        return any(
            attribute_value_is_match(attribute_value, style_value_condition_item) for style_value_condition_item in attribute_value_condition
        )
    if isinstance(attribute_value_condition, Iterable):
        return any(
            attribute_value_is_match(attribute_value, style_value_condition_item) for style_value_condition_item in attribute_value_condition
        )
    if isinstance(attribute_value_condition, Callable):
        predicate_param_count = len(inspect.signature(attribute_value_condition).parameters)
        if predicate_param_count == 1:
            return attribute_value_condition(attribute_value)
        else:
            raise ValueError(f"Unexpected number of parameters for attribute_value_condition: {predicate_param_count}")
    raise TypeError(f"Unexpected type for attribute_value_condition: {type(attribute_value_condition)}")


def style_has_match(style_parsed: Dict[str, str], style_name: str, style_value_condition: Optional[PanfluteElementStyleValuePredicate]) -> bool:
    if style_name not in style_parsed:
        return False

    style_value = style_parsed[style_name]
    if style_value_condition is None:
        return True
    if isinstance(style_value_condition, bool):
        return style_value_condition
    if isinstance(style_value_condition, str):
        return style_value in (style_value_condition, f'"{style_value_condition}"')
    if isinstance(style_value_condition, Sequence):
        return any(
            style_has_match(style_parsed, style_name, style_value_condition_item) for style_value_condition_item in style_value_condition
        )
    if isinstance(style_value_condition, Iterable):
        return any(
            style_has_match(style_parsed, style_name, style_value_condition_item) for style_value_condition_item in style_value_condition
        )
    if isinstance(style_value_condition, Callable):
        predicate_param_count = len(inspect.signature(style_value_condition).parameters)
        if predicate_param_count == 1:
            return style_value_condition(style_value)
        elif predicate_param_count == 2:
            (style_value_value, style_value_unit) = css_unit_pattern.match(style_value).groups()
            style_value_value = float(style_value_value)
            return style_value_condition(style_value_value, style_value_unit)
        else:
            raise ValueError(f"Unexpected number of parameters for style_value_condition: {predicate_param_count}")
    raise TypeError(f"Unexpected type for style_value_condition: {type(style_value_condition)}")


css_unit_pattern = re.compile(r"^(\d*(?:\.\d+)?)\s*(.+)$")
