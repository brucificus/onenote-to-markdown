import functools
import logging
import pathlib
from typing import Tuple

import panflute

from markdown_dom.type_variables import PanfluteElementFilter
from onenote_export.OneNotePageExportTaskContext import OneNotePageExportTaskContext
from onenote_export.page_export_tasks.ElementsUpdateExtractedOrdinatedAssetLocalUrl import \
    _map_ordinated_asset_extraction_path, \
    ElementsUpdateOrdinatedAssetLocalUrl


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
        for element_type in (panflute.Image, panflute.Link):
            element_filters += (ElementsUpdateOrdinatedAssetLocalUrl(
                    element_type=element_type,
                    new_asset_path=new_asset_path,
            ),)

    logger.info(f"📝️️ Updating ordinated asset references in markdown: '{context.output_md_path}'")
    doc.update_via_panflute_filters(element_filters=element_filters)
    logger.info(f"☑️ Updated ordinated asset references in markdown: '{context.output_md_path}'")
