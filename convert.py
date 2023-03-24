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
PROCESS_RECYCLE_BIN = False
LOGFILE = 'onenote_to_markdown.log' # Set to None to disable logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8')
if LOGFILE:
    fh = logging.FileHandler(LOGFILE, mode='w', encoding='utf-8', delay=True)
    fh.setLevel(logging.WARNING)
    logging.root.addHandler(fh)
# For debugging purposes, set this variable to limit which pages are exported:
EXPORT_EXCLUSION_FILTER = r''


def should_handle(node: OneNoteNode) -> bool:
    if not EXPORT_EXCLUSION_FILTER or len(EXPORT_EXCLUSION_FILTER) == 0:
        return True
    if isinstance(node, OneNoteElementBasedNode):
        route_as_lines = os.linesep.join(node.route)
        search_result = re.findall(pattern=EXPORT_EXCLUSION_FILTER, string=route_as_lines, flags= re.IGNORECASE | re.MULTILINE)
        return not search_result or len(search_result) == 0
    return True


if __name__ == "__main__":
    try:
        onenote = OneNoteApplication()
        path_scrubber = PathComponentScrubber()
        exporter = create_default_onenote_exporter(
            root_output_dir=OUTPUT_DIR,
            page_relative_assets_dir=ASSETS_DIR,
            convert_node_name_to_path_component=path_scrubber,
            should_export=should_handle
        )
        exporter.execute_export(onenote)

    except pywintypes.com_error as e:
        traceback.print_exc()
        logging.critical("Hint: Make sure OneNote is open first.", exc_info=True)
