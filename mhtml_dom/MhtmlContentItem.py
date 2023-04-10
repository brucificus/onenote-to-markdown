import pathlib
from typing import Optional, Union

from mhtml_dom.MhtmlContentItemHeaders import MhtmlContentItemHeaders
from onenote_export.Pathlike import Pathlike


class MhtmlContentItem(MhtmlContentItemHeaders):
    def __init__(self, headers: Union[MhtmlContentItemHeaders, dict], body: Optional[Union[str, bytes]]):
        if not headers:
            raise ValueError('No headers provided')
        if isinstance(headers, MhtmlContentItemHeaders):
            headers = headers._headers
        if not isinstance(headers, dict):
            raise ValueError('Headers must be a dictionary')
        if not isinstance(body, (str, bytes, type(None))):
            raise ValueError('Body must be a string or bytes or None')

        super().__init__(headers)
        self._body = body

    def __str__(self):
        result = f'{self.__class__.__name__}('
        if self.content_location:
            result += f'content_location: {self.content_location!r}\n'
        if self.content_type:
            if self.content_type.params:
                result += f'content_type: "{self.content_type.value}; …"\n'
            else:
                result += f'content_type: {self.content_type.value!r}\n'
        if self.content_transfer_encoding:
            result += f'content_transfer_encoding: {self.content_transfer_encoding!r}\n'
        if self.body:
            result += f'body: {self.body!r}\n'
        result = result.rstrip('\n').replace('\n', '; ')
        result += ')'
        return result

    def __repr__(self):
        return self.__str__()

    @property
    def body(self) -> Optional[Union[str, bytes]]:
        return self._body

    def save_to_file(self, file_path: Pathlike, *, overwrite: bool = False):
        if not self.body:
            raise ValueError('No body to save')
        if isinstance(file_path, str):
            file_path = pathlib.Path(file_path)
        if not isinstance(file_path, pathlib.Path):
            raise ValueError('File path must be a string or pathlib.Path')

        if isinstance(self.body, bytes):
            if file_path.exists():
                if not overwrite:
                    raise FileExistsError(f'File already exists: {file_path}')
                with file_path.open('w+b') as file:
                    file.write(self.body)
            else:
                file_path.write_bytes(self.body)
        else:
            encoding = self.content_type.params.charset or 'utf-8'
            if file_path.exists():
                if not overwrite:
                    raise FileExistsError(f'File already exists: {file_path}')
                with file_path.open('w+', encoding=encoding) as file:
                    file.write(self.body)
            else:
                file_path.write_text(self.body, encoding=encoding)
