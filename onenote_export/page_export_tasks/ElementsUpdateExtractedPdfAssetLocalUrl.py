import pathlib
import re
import urllib
from typing import Optional, Iterable

import panflute

from markdown_dom.PanfluteElementPredicateFilterPair import PanfluteElementPredicateFilterPairBase
from markdown_dom.type_variables import PanfluteElementLike, PanfluteElementPredicate, PanfluteElementFilter

broken_image_path_pattern = re.compile(r"image(\d+)\.jpg")


def get_jpg_image_ordinal(element: panflute.Element) -> Optional[int]:
    if not isinstance(element, panflute.Image):
        return None

    found = broken_image_path_pattern.findall(element.url)
    if not found:
        return None

    image_number = int(found[-1])
    return image_number


class ElementsUpdateExtractedPdfAssetLocalUrl(PanfluteElementPredicateFilterPairBase):
    def __init__(self, relative_asset_path: pathlib.Path, image_index: int, *, base_elements_predicate: Optional[PanfluteElementPredicate] = None):
        super().__init__(base_elements_predicate=base_elements_predicate)
        self._relative_asset_path = relative_asset_path
        self._image_index = image_index

    @property
    def _relative_asset_url(self) -> str:
        return urllib.parse.quote(str(self._relative_asset_path).encode('utf8'), safe='\\').replace('\\', '/')

    @property
    def _remaining_element_predicate_clauses(self) -> Iterable[PanfluteElementPredicate]:
        def element_is_image(element: panflute.Element) -> bool:
            return isinstance(element, panflute.Image)

        def image_has_url_for_local_numbered_jpg(element: panflute.Image) -> bool:
            jpg_image_ordinal = get_jpg_image_ordinal(element)
            if jpg_image_ordinal and jpg_image_ordinal == self._image_index + 1:
                return True
            return False

        yield element_is_image
        yield image_has_url_for_local_numbered_jpg

    @property
    def _describe_remaining_element_predicate_clauses(self) -> Optional[str]:
        return f"element is Image with URL for local JPG asset #{self._image_index + 1}"

    @property
    def _element_filter(self) -> PanfluteElementFilter:
        def update_image_url(element: panflute.Element) -> Optional[PanfluteElementLike]:
            element.url = self._new_image_url
        return update_image_url

    @property
    def _describe_element_filter(self) -> str:
        return f"replaces URL such that it now points to '{self._relative_asset_path}'"

    @property
    def _description_emoji_infix(self) -> str:
        return '🖼️'
