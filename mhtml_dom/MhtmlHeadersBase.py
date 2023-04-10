from functools import cache

from typing import Optional

from mhtml_dom.ContentType import ContentType


class MhtmlHeadersBase:
    def __init__(self, headers: dict):
        if not headers:
            raise ValueError('No headers provided')
        if not isinstance(headers, dict):
            raise ValueError('Headers must be a dictionary')

        self._headers = headers

    @property
    @cache
    def content_type(self) -> Optional[ContentType]:
        return ContentType.from_str(self._headers.get('Content-Type')) if 'Content-Type' in self._headers else None
