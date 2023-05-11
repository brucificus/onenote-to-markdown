from typing import Optional, Iterable

import panflute

from markdown_dom.PanfluteElementPredicateFilterPair import PanfluteElementPredicateFilterPairBase
from markdown_dom.type_variables import PanfluteElementPredicate, PanfluteElementFilter
from markdown_re import PanfluteElementLike


class ElementsReparseEmbeddedHtml(PanfluteElementPredicateFilterPairBase):
    def __init__(self, *, base_elements_predicate: Optional[PanfluteElementPredicate] = None):
        super().__init__(base_elements_predicate=base_elements_predicate)

    @property
    def _remaining_element_predicate_clauses(self) -> Iterable[PanfluteElementPredicate]:
        def valid_for_reparse_embedded_html(element: panflute.Element) -> bool:
            return isinstance(element, panflute.RawBlock) and element.format == "html"
        yield valid_for_reparse_embedded_html

    @property
    def _describe_remaining_element_predicate_clauses(self) -> Optional[str]:
        return "element is RawBlock with format 'html'"

    @property
    def _element_filter(self) -> PanfluteElementFilter:
        def reparse_embedded_html(element: panflute.Element, _: panflute.Doc) -> Optional[PanfluteElementLike]:
            new_element = panflute.convert_text(
                text=element.text,
                input_format="html",
                standalone=False,
                output_format="panflute",
                extra_args=[
                    "--wrap=preserve",
                ]
            )
            return new_element
        return reparse_embedded_html

    @property
    def _describe_element_filter(self) -> str:
        return "injects the result of reparsing the embedded HTML"

    @property
    def _description_emoji_infix(self) -> str:
        return '💫'
