from onenote import OneNotePage
from onenote_export.OneNotePageExportError import OneNotePageExportError


class OneNotePageDocxExportError(OneNotePageExportError):
    def __init__(self, page: OneNotePage, e: Exception = None, message: str = None):
        if not message:
            message_suffix = f": {e}" if e is not None else ""
            message = f"Error exporting DOCX for page '{page.name}' ({page.node_id}){message_suffix}"
        super().__init__(page = page, e = e, message = message)
