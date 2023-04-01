import functools
import logging
import os
import re
import traceback
import pywintypes

from onenote import OneNoteApplication, OneNoteNode, OneNoteElementBasedNode
from onenote_export.OneNoteExporter import create_default_onenote_exporter
from path_scrubbing import PathComponentScrubber


OUTPUT_DIR = os.path.join(os.path.expanduser('~'), "Desktop", "OneNoteExport")
ASSETS_DIR = "assets"
USE_LEGACY_DOCX_EXPORT = False
LOGFILE = 'onenote_to_markdown.log' # Set to None to disable logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8')
if LOGFILE:
    fh = logging.FileHandler(LOGFILE, mode='w', encoding='utf-8', delay=True)
    fh.setLevel(logging.WARNING)
    logging.root.addHandler(fh)
# For debugging purposes, set either or both of these variables to limit which pages are exported:
EXPORT_EXCLUSION_FILTER = r''
EXPORT_INCLUSION_FILTER = r''


def should_handle(node: OneNoteNode) -> bool:
    if (not EXPORT_EXCLUSION_FILTER or len(EXPORT_EXCLUSION_FILTER) == 0) \
        and (not EXPORT_INCLUSION_FILTER or len(EXPORT_INCLUSION_FILTER) == 0
    ):
        return True

    if not isinstance(node, OneNoteElementBasedNode):
        return True

    route_as_lines = os.linesep.join(node.route)
    search = functools.partial(re.findall, string=route_as_lines, flags=re.IGNORECASE | re.MULTILINE)

    if EXPORT_INCLUSION_FILTER and len(EXPORT_INCLUSION_FILTER) > 0:
        inclusion_search_result = search(EXPORT_INCLUSION_FILTER)
        if len(inclusion_search_result) == 0:
            return False

    if EXPORT_EXCLUSION_FILTER and len(EXPORT_EXCLUSION_FILTER) > 0:
        exclusion_search_result = search(EXPORT_EXCLUSION_FILTER)
        if len(exclusion_search_result) > 0:
            return False

    return True


if __name__ == "__main__":
    try:
        onenote = OneNoteApplication()
        path_scrubber = PathComponentScrubber()
        exporter = create_default_onenote_exporter(
            root_output_dir=OUTPUT_DIR,
            page_relative_assets_dir=ASSETS_DIR,
            path_component_scrubber=path_scrubber,
            should_export=should_handle,
            use_legacy_docx_export=USE_LEGACY_DOCX_EXPORT,
        )
        exporter.execute_export(onenote)

    except pywintypes.com_error as e:
        traceback.print_exc()
        logging.critical("Hint: Make sure OneNote is open first.", exc_info=True)
