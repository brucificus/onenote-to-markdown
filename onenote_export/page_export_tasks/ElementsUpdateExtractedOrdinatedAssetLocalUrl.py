import pathlib
import re
import urllib.parse
from typing import Optional, Union, Iterable

import panflute

from markdown_dom.PanfluteElementPredicateFilterPair import PanfluteElementPredicateFilterPairBase
from markdown_dom.type_variables import PanfluteElementPredicate, PanfluteElementFilter


asset_ordinal_pattern = re.compile(r'\D+(\d+)\.')


def _get_relative_asset_path_from_href(asset_href_raw: str) -> Optional[pathlib.Path]:
    href_parsed = urllib.parse.urlparse(urllib.parse.unquote(asset_href_raw))
    if href_parsed.scheme or href_parsed.netloc:
        return None
    return pathlib.Path(href_parsed.path)


def _get_href_from_relative_asset_path(relative_asset_path: pathlib.Path) -> str:
    asset_href_bytes = str(relative_asset_path).encode('utf-8')
    asset_href = urllib.parse.quote(asset_href_bytes, safe='\\').replace('\\', '/')
    return asset_href


def _determine_asset_ordinal_from_filename(filename: str) -> Optional[int]:
    numbers_found = asset_ordinal_pattern.findall(filename)
    if not numbers_found:
        return None
    if len(numbers_found) > 1:
        raise ValueError(f"Could not determine asset ordinal from filename: '{filename}'")
    return int(numbers_found[0])


def _map_ordinated_asset_extraction_path(original_extraction_path: pathlib.Path, assets_dir: pathlib.Path, assets_filename_stem_prefix: str) -> Optional[pathlib.Path]:
    if original_extraction_path.suffix in ('.html', '.htm'):
        return None  # Don't extract HTML files.
    original_filename = original_extraction_path.name
    asset_ordinal = _determine_asset_ordinal_from_filename(original_filename)
    if asset_ordinal is None and asset_ordinal != 0:
        return None  # Don't extract files that don't have an ordinal.
    suffix = pathlib.Path(original_filename).suffix
    new_filename = pathlib.Path(f"{assets_filename_stem_prefix}{asset_ordinal:03d}{suffix}")
    return assets_dir / new_filename


class ElementsUpdateOrdinatedAssetLocalUrl(PanfluteElementPredicateFilterPairBase):
    def __init__(self, new_asset_path: pathlib.Path, element_type: type[Union[panflute.Image, panflute.Link]], *, base_elements_predicate: Optional[PanfluteElementPredicate] = None):
        super().__init__(base_elements_predicate=base_elements_predicate)
        self._new_asset_path = new_asset_path
        self._element_type = element_type
        self._asset_ordinal = _determine_asset_ordinal_from_filename(new_asset_path.name)

    @property
    def _new_asset_href(self) -> str:
        return urllib.parse.quote(str(self._new_asset_path).encode('utf8'), safe='\\').replace('\\', '/')

    @property
    def _remaining_element_predicate_clauses(self) -> Iterable[PanfluteElementPredicate]:
        def element_is_expected_type(element: panflute.Element) -> bool:
            return isinstance(element, self._element_type)

        def element_has_url_recognizable_as_for_relative_local_ordinated_asset(element: panflute.Element) -> bool:
            relative_asset_path = _get_relative_asset_path_from_href(element.url)
            if not relative_asset_path:
                return False
            # For the time being, we only support assets that are down one level into a subfolder from the document.
            if len(relative_asset_path.parents) != 2:
                return False
            asset_ordinal_from_filename = _determine_asset_ordinal_from_filename(relative_asset_path.name)
            return asset_ordinal_from_filename == self._asset_ordinal

        yield element_is_expected_type
        yield element_has_url_recognizable_as_for_relative_local_ordinated_asset

    @property
    def _describe_remaining_element_predicate_clauses(self) -> Optional[str]:
        return f"element is '{self._element_type.__name__}' and has URL recognizable as for relative local asset #{self._asset_ordinal}"

    @property
    def _element_filter(self) -> PanfluteElementFilter:
        def update_element_relative_url_to_local_asset(element: panflute.Element, _: panflute.Doc) -> Optional[panflute.Element]:
            element.url = self._new_asset_href
            return element
        return update_element_relative_url_to_local_asset

    @property
    def _describe_element_filter(self) -> str:
        return f"replaces URL such that it now points to local asset '{self._new_asset_path}'"

    @property
    def _description_emoji_infix(self) -> str:
        return '✂️️'
