from typing import Sequence, Iterable

from markdown_dom.PanfluteElementPredicateFilterPair import PanfluteElementPredicateFilterPair, \
    AbstractPanfluteElementPredicateFilterPair
from markdown_dom.type_variables import PanfluteElementPredicate
from onenote_export.OneNotePageExporterSettings import OneNotePageContentExportStyleSettings, \
    OneNotePageContentExportClassSettings, OneNotePageContentStyleExportElementClassRemovals, \
    OneNotePageContentStyleExportElementClassElementPushes, OneNotePageContentStyleExportElementStyleRemovals, \
    OneNotePageContentStyleExportElementStyleElementPushes
from onenote_export.page_export_tasks.ElementsPushSpecificClass import ElementsPushSpecificClass
from onenote_export.page_export_tasks.ElementsPushSpecificStyle import ElementsPushSpecificStyle
from onenote_export.page_export_tasks.ElementsRemoveSpecificClass import ElementsRemoveSpecificClass
from onenote_export.page_export_tasks.ElementsRemoveSpecificStyle import ElementsRemoveSpecificStyle
from onenote_export.page_export_tasks._element_predicates import element_is_table_element_in_gridlike_table, \
    element_is_table_element_in_table, element_is_div_with_any_classes, element_has_classes, element_is_div_with_any_style, \
    element_has_style


def _create_styling_element_predicate_filter_pairs(style_settings: OneNotePageContentExportStyleSettings, class_settings: OneNotePageContentExportClassSettings) -> Sequence[PanfluteElementPredicateFilterPair]:
    def create_class_removers(base_elements_predicate: PanfluteElementPredicate, removals: OneNotePageContentStyleExportElementClassRemovals) -> Iterable[AbstractPanfluteElementPredicateFilterPair]:
        for class_to_remove in removals:
            yield ElementsRemoveSpecificClass(class_to_remove=class_to_remove, base_elements_predicate=base_elements_predicate)

    def create_class_pushers(base_elements_predicate: PanfluteElementPredicate, pushes: OneNotePageContentStyleExportElementClassElementPushes) -> Iterable[AbstractPanfluteElementPredicateFilterPair]:
        for class_to_push in pushes:
            yield ElementsPushSpecificClass(class_to_push=class_to_push, new_child_element_type=pushes[class_to_push],
                                            base_elements_predicate=base_elements_predicate)

    def create_style_removers(base_elements_predicate: PanfluteElementPredicate, removals: OneNotePageContentStyleExportElementStyleRemovals) -> Iterable[AbstractPanfluteElementPredicateFilterPair]:
        for style_to_remove in removals:
            style_value_removal_condition = removals[style_to_remove]
            yield ElementsRemoveSpecificStyle(style_to_remove=style_to_remove,
                                              style_value_removal_condition=style_value_removal_condition,
                                              base_elements_predicate=base_elements_predicate)

    def create_specific_style_pushers(base_elements_predicate: PanfluteElementPredicate, pushes: OneNotePageContentStyleExportElementStyleElementPushes) -> Iterable[AbstractPanfluteElementPredicateFilterPair]:
        for style_to_push in pushes:
            for style_value_to_push in pushes[style_to_push]:
                yield ElementsPushSpecificStyle(style_to_push=style_to_push, style_value_to_push=style_value_to_push,
                                                new_child_element_type=pushes[style_to_push][style_value_to_push],
                                                base_elements_predicate=base_elements_predicate)

    style_and_class_updating_element_predicate_filter_pairs: Sequence[AbstractPanfluteElementPredicateFilterPair] = (
        *create_class_removers(element_is_table_element_in_gridlike_table, removals=class_settings.gridlike_table_elements.removals),
        *create_class_removers(element_is_table_element_in_table, removals=class_settings.all_table_elements.removals),
        *create_class_removers(element_is_div_with_any_classes, removals=class_settings.divs.removals),
        *create_class_removers(element_has_classes, removals=class_settings.all_elements.removals),

        *create_class_pushers(element_is_table_element_in_gridlike_table, pushes=class_settings.gridlike_table_elements.pushes),
        *create_class_pushers(element_is_table_element_in_table, pushes=class_settings.all_table_elements.pushes),
        *create_class_pushers(element_is_div_with_any_classes, pushes=class_settings.divs.pushes),
        *create_class_pushers(element_has_classes, pushes=class_settings.all_elements.pushes),

        *create_style_removers(element_is_table_element_in_gridlike_table, removals=style_settings.gridlike_table_elements.removals),
        *create_style_removers(element_is_table_element_in_table, removals=style_settings.all_table_elements.removals),
        *create_style_removers(element_is_div_with_any_style, removals=style_settings.divs.removals),
        *create_style_removers(element_has_style, removals=style_settings.all_elements.removals),

        *create_specific_style_pushers(element_is_table_element_in_gridlike_table, pushes=style_settings.gridlike_table_elements.pushes),
        *create_specific_style_pushers(element_is_table_element_in_table, pushes=style_settings.all_table_elements.pushes),
        *create_specific_style_pushers(element_is_div_with_any_style, pushes=style_settings.divs.pushes),
        *create_specific_style_pushers(element_has_style, pushes=style_settings.all_elements.pushes),
    )

    return style_and_class_updating_element_predicate_filter_pairs
