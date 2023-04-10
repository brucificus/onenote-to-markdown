from typing import Optional

from mhtml_dom.MhtmlHeadersBase import MhtmlHeadersBase


class MhtmlContentItemHeaders(MhtmlHeadersBase):
    def __init__(self, headers: dict):
        if not headers:
            raise ValueError('No headers provided')
        if not isinstance(headers, dict):
            raise ValueError('Headers must be a dictionary')

        super().__init__(headers)

    @property
    def content_location(self) -> Optional[str]:
        return self._headers.get('Content-Location') if 'Content-Location' in self._headers else None

    @property
    def content_transfer_encoding(self) -> Optional[str]:
        return self._headers.get('Content-Transfer-Encoding') if 'Content-Transfer-Encoding' in self._headers else None
