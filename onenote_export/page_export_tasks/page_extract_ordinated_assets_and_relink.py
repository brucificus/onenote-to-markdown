import functools
import logging
import pathlib
import re
import urllib.parse

from typing import Tuple, Optional, Union

import panflute

from markdown_dom.type_variables import PanfluteElementFilter
from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext


asset_ordinal_pattern = re.compile(r'\D+(\d+)\.')


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
    else:
        suffix = pathlib.Path(original_filename).suffix
        new_filename = pathlib.Path(f"{assets_filename_stem_prefix}{asset_ordinal:03d}{suffix}")
        return assets_dir / new_filename


def _get_relative_asset_path_from_href(asset_href_raw: str) -> Optional[pathlib.Path]:
    href_parsed = urllib.parse.urlparse(urllib.parse.unquote(asset_href_raw))
    if href_parsed.scheme or href_parsed.netloc:
        return None
    return pathlib.Path(href_parsed.path)


def _get_href_from_relative_asset_path(relative_asset_path: pathlib.Path) -> str:
    asset_href_bytes = str(relative_asset_path).encode('utf-8')
    asset_href = urllib.parse.quote(asset_href_bytes, safe='\\').replace('\\', '/')
    return asset_href


def _update_element_relative_url_to_local_asset(
    element: panflute.Element,
    _: panflute.Doc,
    asset_ordinal: int,
    new_asset_href: str,
    element_type: type[Union[panflute.Image, panflute.Link]],
) -> Optional[panflute.Element]:
    if not isinstance(element, element_type):
        return element
    relative_asset_path = _get_relative_asset_path_from_href(element.url)
    if not relative_asset_path:
        return element

    # For the time being, we only support assets that are down one level into a subfolder from the document.
    if len(relative_asset_path.parents) != 2:
        return element

    asset_ordinal_from_filename = _determine_asset_ordinal_from_filename(relative_asset_path.name)
    if asset_ordinal_from_filename != asset_ordinal:
        return element

    element.url = new_asset_href
    return element


def page_extract_ordinated_assets_and_relink(context: OneNotePageExportTaskContext, logger: logging.Logger):
    assets_filename_stem_prefix = context.safe_filename_base.stem + '_'
    map_asset_extraction_path = functools.partial(
        _map_ordinated_asset_extraction_path,
        assets_dir=pathlib.Path(context.assets_dir),
        assets_filename_stem_prefix=assets_filename_stem_prefix
    )

    logger.info(f"✂️️ Extracting ordinated assets: '{context.output_md_path}'")
    extracted_assets = context.extract_assets_to(
        target_dir=context.output_dir,
        map_extraction_path=map_asset_extraction_path,
    )

    logger.info(f"️🗺️ Preparing to update ordinated asset references in markdown: '{context.output_md_path}'")
    doc = context.output_md_document
    element_filters: Tuple[PanfluteElementFilter, ...] = ()

    for new_asset_path in extracted_assets:
        asset_ordinal = _determine_asset_ordinal_from_filename(new_asset_path.name)
        asset_href = _get_href_from_relative_asset_path(new_asset_path)

        for element_type in (panflute.Image, panflute.Link):
            element_filter: PanfluteElementFilter = functools.partial(
                _update_element_relative_url_to_local_asset,
                asset_ordinal=asset_ordinal,
                new_asset_href=asset_href,
                element_type=element_type
            )
            element_filters += (element_filter,)

    logger.info(f"📝️️ Updating ordinated asset references in markdown: '{context.output_md_path}'")
    doc.update_via_panflute_filters(element_filters=element_filters)
    logger.info(f"☑️ Updated ordinated asset references in markdown: '{context.output_md_path}'")
