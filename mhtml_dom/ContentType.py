from email.message import Message

from typing import Optional

from mhtml_dom.ContentTypeParams import ContentTypeParams


class ContentType:
    def __init__(self, value: str, params: ContentTypeParams = None):
        if not value:
            raise ValueError('value is empty')
        if params is None:
            params = ContentTypeParams()
        if not isinstance(params, ContentTypeParams):
            raise ValueError('params must be a ContentTypeParams')

        self._value = value
        self._params = params or ContentTypeParams()

    @property
    def value(self) -> str:
        return self._value

    @property
    def params(self) -> ContentTypeParams:
        return self._params

    def __eq__(self, other):
        if isinstance(other, str):
            return self == ContentType.from_str(other)
        if isinstance(other, ContentType):
            return self.value == other.value and self.params == other.params
        return False

    def __hash__(self):
        return hash((self.value, self.params))

    def __str__(self):
        if self.params:
            return f'{self.value}; {self.params}'
        return self.value

    def __repr__(self):
        if self.params:
            return f'{self.__class__.__name__}({self.value!r}, {self.params!r})'
        return f'{self.__class__.__name__}({self.value!r})'

    @classmethod
    def from_str(cls, content_type: str) -> 'ContentType':
        email = Message()
        email['Content-Type'] = content_type
        content_type, content_type_params = email.get_content_type(), email.get_params()
        if content_type_params[0][1] == '' and content_type_params[0][0] == content_type:
            content_type_params = content_type_params[1:]
        return cls(content_type, ContentTypeParams(dict(content_type_params)))

    def suggest_file_suffix(self) -> Optional[str]:
        if self.value == 'text/html':
            return '.html'
        if self.value == 'text/plain':
            return '.txt'
        if self.value == 'image/png':
            return '.png'
        if self.value == 'image/jpeg':
            return '.jpg'
        if self.value == 'image/gif':
            return '.gif'
        if self.value == 'image/svg+xml':
            return '.svg'
        if self.value == 'application/pdf':
            return '.pdf'
        if self.value == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return '.docx'
        if self.value == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            return '.xlsx'
        if self.value == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
            return '.pptx'
        if self.value == 'application/vnd.ms-excel':
            return '.xls'
        if self.value == 'application/vnd.ms-powerpoint':
            return '.ppt'
        if self.value == 'application/msword':
            return '.doc'
        if self.value == 'application/zip':
            return '.zip'
        if self.value == 'application/x-rar-compressed':
            return '.rar'
        if self.value == 'application/x-tar':
            return '.tar'
        if self.value == 'application/x-gzip':
            return '.gz'
        if self.value == 'application/x-bzip2':
            return '.bz2'
        if self.value == 'application/x-7z-compressed':
            return '.7z'
        if self.value == 'application/x-xz':
            return '.xz'
        if self.value == 'application/x-lzma':
            return '.lzma'
        if self.value == 'application/x-lzip':
            return '.lzip'
        if self.value == 'application/x-lzop':
            return '.lzop'
        if self.value == 'application/x-bzip':
            return '.bz'
        return None
