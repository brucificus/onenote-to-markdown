from datetime import datetime

from typing import Optional

from mhtml_dom.MhtmlHeadersBase import MhtmlHeadersBase


class MhtmlContainerHeaders(MhtmlHeadersBase):
    def __init__(self, headers: dict):
        if not headers:
            raise ValueError('No headers provided')
        if not isinstance(headers, dict):
            raise ValueError('Headers must be a dictionary')

        self._headers = headers

    @property
    def from_(self) -> Optional[str]:
        return self._headers.get('From') if 'From' in self._headers else None

    @property
    def subject(self) -> Optional[str]:
        return self._headers.get('Subject') if 'Subject' in self._headers else None

    @property
    def mime_version(self) -> Optional[str]:
        return self._headers.get('MIME-Version') if 'MIME-Version' in self._headers else None

    @property
    def date(self) -> Optional[datetime]:
        return datetime.strptime(self._headers.get('Date'), '%a, %d %b %Y %H:%M:%S %z') if 'Date' in self._headers else None

    @property
    def snapshot_content_location(self) -> Optional[str]:
        return self._headers.get('Snapshot-Content-Location') if 'Snapshot-Content-Location' in self._headers else None
