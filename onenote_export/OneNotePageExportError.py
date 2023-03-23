from onenote import OneNotePage


class OneNotePageExportError(Exception):
    def __init__(self, page: OneNotePage, e: Exception = None, message: str = None):
        if not message:
            message_suffix = f": {e}" if e is not None else ""
            message = f"Error exporting page '{page.name}' ({page.node_id}){message_suffix}"
        super().__init__(message, e)
        self._page = page

    @property
    def page(self) -> OneNotePage:
        return self._page
